import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from functools import wraps

import httpx
import jwt
import redis.exceptions
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import inspect

from app.core.config import CACHE_ENABLED, DEBUG, JWT_SECRET_KEY, REDIS_TIMEOUT, USE_VERCEL_KV
from app.core.utils import normalize_query
from app.features.user.models import User

app_logger = logging.getLogger("app")

if DEBUG:
    app_logger.setLevel(logging.DEBUG)
else:
    app_logger.setLevel(logging.INFO)

if not app_logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:     [%(name)s] %(message)s"))
    app_logger.addHandler(handler)


# На Vercel змінна VERCEL_ENV завжди проставлена платформою автоматично
# (production / preview / development). Якщо ми в продакшені, а KV не
# налаштовано (забули додати env var, чи DEBUG випадково truthy) — краще
# впасти одразу на старті, ніж мовчки бити кожен запит у localhost:6379.
if os.getenv("VERCEL_ENV") == "production":
    if not CACHE_ENABLED:
        raise RuntimeError("CACHE_ENABLED=false заборонено в продакшені — це локальна опція для розробки.")
    if not USE_VERCEL_KV:
        raise RuntimeError(
            "KV_REST_API_URL / KV_REST_API_TOKEN не налаштовані в продакшені. "
            "Кеш не може мовчки фолбекнутись на localhost Redis у Vercel."
        )

redis_client = None

if not CACHE_ENABLED:
    app_logger.info("CACHE_ENABLED=false — кешування вимкнено, Redis/Docker не потрібен.")
elif USE_VERCEL_KV and not DEBUG:
    # Production version
    from upstash_redis.asyncio import Redis as UpstashRedis

    redis_client = UpstashRedis(url=os.getenv("KV_REST_API_URL"), token=os.getenv("KV_REST_API_TOKEN"))
    app_logger.debug("Redis type: Vercel KV (Upstash Redis)")
else:
    # Local test
    import redis.asyncio as local_redis

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = local_redis.from_url(REDIS_URL, decode_responses=True)
    app_logger.debug("Redis type: Redis (Local test)")


async def _safe_redis_get(cache_key: str):
    """
    Обгортка над redis_client.get з таймаутом і широким перехопленням
    помилок. Кеш ніколи не має ламати запит — при будь-якій проблемі
    (мережа, таймаут, несумісна відповідь upstash) повертаємо None і
    йдемо в БД, як при звичайному промаху кешу.
    """
    if redis_client is None:  # CACHE_ENABLED=false
        return None
    try:
        return await asyncio.wait_for(redis_client.get(cache_key), timeout=REDIS_TIMEOUT)
    except asyncio.TimeoutError:
        app_logger.warning("Redis read timeout (%.1fs) for key %s", REDIS_TIMEOUT, cache_key)
    except (redis.exceptions.RedisError, httpx.HTTPError) as e:
        app_logger.warning("Redis read error (%s): %s", type(e).__name__, e)
    except (OSError, ValueError) as e:
        app_logger.warning("Unexpected Redis read error (%s): %s", type(e).__name__, e)
    return None


async def _safe_redis_set(cache_key: str, value: str, ttl: int) -> None:
    if redis_client is None:  # CACHE_ENABLED=false
        return
    try:
        await asyncio.wait_for(redis_client.set(cache_key, value, ex=ttl), timeout=REDIS_TIMEOUT)
    except asyncio.TimeoutError:
        app_logger.warning("Redis write timeout (%.1fs) for key %s", REDIS_TIMEOUT, cache_key)
    except (redis.exceptions.RedisError, httpx.HTTPError) as e:
        app_logger.warning("Redis write error (%s): %s", type(e).__name__, e)
    except (OSError, ValueError) as e:
        app_logger.warning("Unexpected Redis write error (%s): %s", type(e).__name__, e)


async def _safe_redis_delete(cache_key: str) -> None:
    if redis_client is None:  # CACHE_ENABLED=false
        return
    try:
        await asyncio.wait_for(redis_client.delete(cache_key), timeout=REDIS_TIMEOUT)
        app_logger.debug("Cache cleared for %s", cache_key)
    except asyncio.TimeoutError:
        app_logger.warning("Redis delete timeout (%.1fs) for key %s", REDIS_TIMEOUT, cache_key)
    except (redis.exceptions.RedisError, httpx.HTTPError) as e:
        app_logger.warning("Redis delete error (%s): %s", type(e).__name__, e)
    except (OSError, ValueError) as e:
        app_logger.warning("Unexpected Redis delete error (%s): %s", type(e).__name__, e)


def cache_site_response(ttl: int = 3600, normalizing: bool = False):
    """
    Асинхронний декоратор для кешування відповідей FastAPI.
    З метою оптимізації швидкодії відповіді сервера створено декоратор
    який має зберігати в redis-cache на vercel side запити від користувачів
    це мають бути загальні запити на сайт (наприклад. : найчастіші 20 сторінок)
    або кешування даних про користувача, щоб кожний раз не звертатись до БД

    ЗАБОРОНЕНО використовувати на POST, PUT, PATCH або DELETE методи
    Декоратор @cache_response має стояти ПІД декоратором маршруту @app.get(...)
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                return await func(*args, **kwargs)

            # Генерація ключа на основі шляху та query-параметрів
            query_string = normalize_query(request.url.query) if normalizing else request.url.query
            cache_key = f"cache:{request.url.path}"
            if query_string:
                cache_key += f"?{query_string}"

            app_logger.debug("cache_key: %s", cache_key)

            # Перевірка в Redis (з таймаутом, ніколи не кидає виняток)
            cached_data = await _safe_redis_get(cache_key)
            if cached_data:
                try:
                    return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
                except (TypeError, json.JSONDecodeError) as e:
                    app_logger.warning("Corrupted cache value for %s (%s): %s", cache_key, type(e).__name__, e)

            # Виконання основної функції
            response_data = await func(*args, **kwargs)

            # Асинхронне збереження в Redis
            try:
                json_compatible_data = jsonable_encoder(response_data)
                await _safe_redis_set(cache_key, json.dumps(json_compatible_data), ttl)
            except (TypeError, ValueError) as e:
                app_logger.warning("Could not serialize response for %s (%s): %s", cache_key, type(e).__name__, e)

            return response_data

        return wrapper

    return decorator


def cache_user_data(ttl: int = 900):
    """
    Декоратор кешування для запитів, які є найчастішими для користувача, такі як favorite.get()
    :param ttl: час життя кешу
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")

            if not current_user or not hasattr(current_user, "id"):
                return await func(*args, **kwargs)

            cache_key = f"user_data:{func.__name__}:{current_user.id}"

            cached_data = await _safe_redis_get(cache_key)
            if cached_data:
                try:
                    app_logger.debug("Cache hit for %s", cache_key)
                    return json.loads(cached_data) if isinstance(cached_data, str) else cached_data
                except (TypeError, json.JSONDecodeError) as e:
                    app_logger.warning("Corrupted cache value for %s (%s): %s", cache_key, type(e).__name__, e)

            response_data = await func(*args, **kwargs)

            if response_data is not None:
                try:
                    json_compatible_data = jsonable_encoder(response_data)
                    await _safe_redis_set(cache_key, json.dumps(json_compatible_data), ttl)
                except (TypeError, ValueError) as e:
                    app_logger.warning("Could not serialize response for %s (%s): %s", cache_key, type(e).__name__, e)

            return response_data

        return wrapper

    return decorator


# Поля User, які можна безпечно класти в Redis. Свідомо НЕ використовуємо
# jsonable_encoder(user) — він серіалізує ВСІ колонки моделі, включно з
# password, а relationships (favorites/orders/cart) при доступі поза
# сесією валять DetachedInstanceError/MissingGreenlet. Беремо лише
# фактичні колонки (без relationships) і явно виключаємо password.
_USER_CACHE_EXCLUDE_FIELDS = {"password"}


def _serialize_user_for_cache(user: User) -> dict:
    mapper = inspect(user).mapper
    return {
        column.key: getattr(user, column.key)
        for column in mapper.column_attrs
        if column.key not in _USER_CACHE_EXCLUDE_FIELDS
    }


def cache_user_token(ttl: int = 900):
    """
    Декоратор зроблений із метою оптимізаії звернень за токеном доступу
    до викликів api/dependencies/get_current_user()
    :param ttl: час життя кешу
    :return:
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            # Request відсутній, значить ми виконуємо функцію без кешування
            if not request:
                return await func(*args, **kwargs)

            token = request.cookies.get("access_token")
            if not token:
                return await func(*args, **kwargs)

            # Декодуємо один раз: беремо exp (щоб не кешувати довше, ніж
            # живе сам токен) і перевіряємо type, щоб не витрачати запит
            # у Redis на завідомо непридатний (наприклад, refresh) токен —
            # func() однаково відхилить його з 401.
            try:
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
            except jwt.PyJWTError:
                return await func(*args, **kwargs)

            if payload.get("type") != "access":
                return await func(*args, **kwargs)

            exp = payload.get("exp", 0)
            remaining = int(exp - datetime.now(timezone.utc).timestamp())
            if remaining <= 0:
                return await func(*args, **kwargs)

            effective_ttl = min(ttl, remaining)
            cache_key = f"auth:token:{hashlib.sha256(token.encode()).hexdigest()}"

            cached_user = await _safe_redis_get(cache_key)
            if cached_user:
                try:
                    user_dict = json.loads(cached_user) if isinstance(cached_user, str) else cached_user
                    app_logger.debug("Cache hit for %s", cache_key)
                    return User(**user_dict)
                except (TypeError, json.JSONDecodeError) as e:
                    app_logger.warning("Corrupted cache value for %s (%s): %s", cache_key, type(e).__name__, e)

            user = await func(*args, **kwargs)
            if user:
                try:
                    safe_user = _serialize_user_for_cache(user)
                    await _safe_redis_set(cache_key, json.dumps(safe_user, default=str), effective_ttl)
                except (TypeError, ValueError) as e:
                    app_logger.warning("Could not serialize user for %s (%s): %s", cache_key, type(e).__name__, e)
            return user

        return wrapper

    return decorator


async def clear_user_cache(func_name: str, user_id: int):
    """
    Допоміжна функція для очищення кешу конкретного користувача після зміни даних (POST, DELETE).
    """
    cache_key = f"user_data:{func_name}:{user_id}"
    await _safe_redis_delete(cache_key)


async def invalidate_token_cache(token: str) -> None:
    """
    Видаляє закешованого користувача для конкретного access-токена.
    Викликати при logout, зміні пароля чи бані користувача — інакше
    закешований `get_current_user` продовжить авторизувати цей токен
    ще до effective_ttl секунд (максимум 15 хв за замовчуванням).
    """
    cache_key = f"auth:token:{hashlib.sha256(token.encode()).hexdigest()}"
    await _safe_redis_delete(cache_key)
