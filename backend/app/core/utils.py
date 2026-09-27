from urllib.parse import unquote


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
