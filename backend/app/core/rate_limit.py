import asyncio

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.dependencies import get_current_user
from app.core.cache import (
    _safe_redis_delete,
    _safe_redis_get,
    _safe_redis_incr,
    _safe_redis_set,
    _safe_redis_ttl,
    app_logger,
    redis_client,
)
from app.core.config import (
    BOT_BLOCK_ENABLED,
    GLOBAL_RATE_LIMIT,
    IP_BAN_SECONDS,
    IP_BAN_STRIKES,
    ON_VERCEL,
    RATE_LIMIT_ENABLED,
    TRUST_PROXY_HEADERS,
)
from app.features.user.models import User

TOO_MANY_REQUESTS_DETAIL = "Too many requests, please try again later"
STRIKES_WINDOW = 3600
LOGIN_WINDOW = 900
# Monobank має завжди достукатись до вебхука, інакше статус оплати не оновиться
SKIP_PATHS = {"/orders/webhook/monobank"}
# shortcut: ловить лише лінивих ботів; бот з браузерним UA впирається в rate limit.
# "bot/" а не "bot": голий підрядок ловив реальні телефони (CUBOT_X30), краулери ж пишуть "Googlebot/2.1"
BOT_UA_MARKERS = (
    "curl",
    "wget",
    "python-requests",
    "python-urllib",
    "aiohttp",
    "httpx",
    "scrapy",
    "go-http-client",
    "java/",
    "libwww",
    "headlesschrome",
    "phantomjs",
    "bot/",
    "+http",
    "spider",
    "crawl",
)


if RATE_LIMIT_ENABLED and redis_client is None:
    app_logger.warning("RATE_LIMIT_ENABLED, але Redis вимкнено (CACHE_ENABLED=false) — rate limit і бани не працюють")


def too_many_requests(retry_after: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=TOO_MANY_REQUESTS_DETAIL,
        headers={"Retry-After": str(retry_after)},
    )


def client_ip(request: Request) -> str | None:
    """None, якщо IP невідомий: тоді не лімітуємо, інакше всі такі запити ділили б один лічильник і бан."""
    if TRUST_PROXY_HEADERS:
        # Vercel сам перезаписує x-real-ip. Інші проксі (Render) дописують побачений IP у КІНЕЦЬ
        # X-Forwarded-For, а початок списку контролює клієнт.
        # shortcut: рахує лише один проксі; якщо перед платформою стане ще один (Cloudflare) — брати його заголовок
        real_ip = request.headers.get("x-real-ip") if ON_VERCEL else None
        if real_ip:
            return real_ip.strip() or None
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[-1].strip() or None
    return request.client.host if request.client else None


def is_bot(user_agent: str | None) -> bool:
    ua = (user_agent or "").lower()
    return not ua or any(marker in ua for marker in BOT_UA_MARKERS)


async def is_ip_banned(ip: str) -> bool:
    return bool(await _safe_redis_get(f"ban:ip:{ip}"))


# shortcut: фіксоване вікно, на межі вікон можна встигнути 2x ліміт; перейти на sliding window, якщо це стане проблемою
async def over_limit(key: str, bucket: str, limit: int, window: int, strike: bool = False) -> bool:
    """
    True, якщо key перевищив limit запитів за window секунд.
    strike=True (лише глобальний ліміт по IP): перше перевищення у вікні дає один страйк, решта 429 того ж
    вікна — ні, щоб один сплеск зі спільного IP кампусу не банив усіх. IP_BAN_STRIKES страйків за годину -> бан.
    """
    count = await _safe_redis_incr(f"rl:{bucket}:{key}", window)
    if count <= limit:
        return False
    if strike and count == limit + 1 and await _safe_redis_incr(f"strikes:{key}", STRIKES_WINDOW) >= IP_BAN_STRIKES:
        await _safe_redis_set(f"ban:ip:{key}", "1", IP_BAN_SECONDS)
        app_logger.warning("IP %s banned for %ss after repeated rate limit hits", key, IP_BAN_SECONDS)
    return True


def rate_limit(bucket: str, limit: int, window: int, per_user: bool = False):
    """
    Залежність FastAPI: dependencies=[Depends(rate_limit("login", 30, 60))].
    Без страйків: на спільному IP кампусу звичайне користування може впертись у ліміт маршруту,
    і це не має банити весь кампус. Бан дає лише глобальний ліміт у security_middleware.
    per_user=True для маршрутів із логіном: ліміт на користувача, а не на спільний IP.
    """
    if per_user:

        async def user_dependency(current_user: User = Depends(get_current_user)) -> None:
            if RATE_LIMIT_ENABLED and await over_limit(f"user:{current_user.id}", bucket, limit, window):
                raise too_many_requests(window)

        return user_dependency

    async def ip_dependency(request: Request) -> None:
        ip = client_ip(request)
        if RATE_LIMIT_ENABLED and ip and await over_limit(ip, bucket, limit, window):
            raise too_many_requests(window)

    return ip_dependency


def _login_keys(email: str, ip: str | None) -> tuple[tuple[str, int], ...]:
    # Пара email+IP — жорсткий ліміт; сам email — м'якший, проти підбору з багатьох IP,
    # і щоб заблокувати чужий вхід треба було 30 запитів, а не 5. Успішний вхід скидає обидва
    email = email.lower()
    return (f"rl:login:{email}:{ip}", 5), (f"rl:login-email:{email}", 30)


async def reserve_login_attempt(email: str, ip: str | None) -> None:
    """
    Рахує спробу ДО перевірки пароля: перевірка «прочитав — потім записав» пропускала б паралельні
    спроби, бо всі вони бачили б старий лічильник, поки йде bcrypt.
    """
    if not RATE_LIMIT_ENABLED:
        return
    keys = _login_keys(email, ip)
    counts = await asyncio.gather(*(_safe_redis_incr(key, LOGIN_WINDOW) for key, _ in keys))
    exceeded = [key for count, (key, limit) in zip(counts, keys) if count > limit]
    if exceeded:
        raise too_many_requests(await _safe_redis_ttl(exceeded[0]) or LOGIN_WINDOW)


async def reset_login_attempts(email: str, ip: str | None) -> None:
    if RATE_LIMIT_ENABLED:
        await asyncio.gather(*(_safe_redis_delete(key) for key, _ in _login_keys(email, ip)))


async def security_middleware(request: Request, call_next):
    if not RATE_LIMIT_ENABLED or request.method == "OPTIONS" or request.url.path in SKIP_PATHS:
        return await call_next(request)

    if BOT_BLOCK_ENABLED and is_bot(request.headers.get("user-agent")):
        return JSONResponse({"detail": "Access denied"}, status_code=status.HTTP_403_FORBIDDEN)

    ip = client_ip(request)
    if not ip:
        return await call_next(request)
    # Бан перевіряємо ДО лічильника: інакше заблокований IP і далі збирав би страйки й продовжував собі бан.
    # shortcut: 2 послідовні команди Upstash на запит; якщо рахунок чи затримка виростуть — перенести
    # глобальний ліміт у Vercel Firewall / WAF
    if await is_ip_banned(ip):
        return JSONResponse({"detail": "Access temporarily blocked"}, status_code=status.HTTP_403_FORBIDDEN)
    if await over_limit(ip, "global", GLOBAL_RATE_LIMIT, 60, strike=True):
        exc = too_many_requests(60)
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)
    return await call_next(request)
