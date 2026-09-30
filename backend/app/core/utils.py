from urllib.parse import unquote

from fastapi import HTTPException, UploadFile, status

ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024


def normalize_query(text: str) -> str:
    """
    Нормалізація тексту запиту до загального вигляду
    :param text: Не нормалізовний текст
    :return: str
    """
    if not text:
        return ""

    # Декодуємо URL-кодування (напр. %20 -> пробіл, кирилицю з %-формату)
    text = unquote(text)

    # Переводимо в нижній регістр (casefold краще за lower для загального пошуку)
    text = text.casefold()

    # Видаляємо пробіли по краях і замінюємо множинні пробіли між словами на один
    text = " ".join(text.split())

    return text


def require_cloudinary(cloudinary_url: str | None) -> None:
    """Перевіряє що CLOUDINARY_URL налаштовано, інакше кидає 503."""
    if not cloudinary_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Робота з фото недоступна: не налаштовано CLOUDINARY_URL",
        )


async def validate_image_file(file: UploadFile) -> bytes:
    """
    Перевіряє тип і розмір завантажуваного зображення.
    Повертає байти файлу або кидає HTTPException.
    """
    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дозволені лише зображення JPEG, PNG або WebP",
        )

    content = await file.read()

    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл порожній")

    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Максимальний розмір фото — 5 МБ",
        )

    return content
