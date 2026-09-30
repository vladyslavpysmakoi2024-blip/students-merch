import random

TSHIRTS = [
    {"id": "tee-campus", "name": "Футболка «Кампус»", "color": "Графітова"},
    {"id": "tee-vibe", "name": "Футболка «Вайб»", "color": "Молочна"},
]

TOTES = [
    {"id": "tote-notes", "name": "Шопер «Конспект»", "color": "Бежевий"},
    {"id": "tote-session", "name": "Шопер «Сесія»", "color": "Чорний"},
    {"id": "tote-break", "name": "Шопер «Перерва»", "color": "Джинсовий"},
]

PACKAGE_PRICE = 1000
SURVEY_DISCOUNT_PERCENT = 15

SURVEY_PACKAGES: list[dict] = [
    {
        "id": f"{tshirt['id']}__{tote['id']}",
        "tshirt": tshirt,
        "tote": tote,
        "price": PACKAGE_PRICE,
        "discountPercent": SURVEY_DISCOUNT_PERCENT,
        "discountedPrice": round(PACKAGE_PRICE * (1 - SURVEY_DISCOUNT_PERCENT / 100)),
    }
    for tshirt in TSHIRTS
    for tote in TOTES
]

AVAILABLE_PACKAGE_IDS: list[str] = [pack["id"] for pack in SURVEY_PACKAGES]


def get_random_package_id() -> str:
    return random.choice(AVAILABLE_PACKAGE_IDS)


def get_package_by_id(package_id: str | None) -> dict | None:
    if not package_id:
        return None
    for pack in SURVEY_PACKAGES:
        if pack["id"] == package_id:
            return pack
    return None
