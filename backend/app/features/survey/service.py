import random

from sqlalchemy.ext.asyncio import AsyncSession

import app.features.clothing.crud as crud_clothing
from app.core.colors import color_name
from app.features.clothing.models import Clothing

SURVEY_DISCOUNT_PERCENT = 15
MAX_PACKAGES_COUNT = 6


def _serialize_item(item: Clothing) -> dict:
    c_name = color_name(item.color) or item.color
    photo = item.photos[0] if (item.photos and len(item.photos) > 0) else None
    return {
        "id": item.id,
        "name": item.name,
        "type": item.type,
        "color": c_name,
        "color_hex": item.color,
        "price": float(item.price),
        "photo": photo,
        "photos": item.photos or [],
    }


async def get_dynamic_packages(db: AsyncSession) -> list[dict]:
    clothes = await crud_clothing.get_available_clothes(db)
    if not clothes:
        return []

    tshirts = [
        c
        for c in clothes
        if "футболк" in (c.type or "").lower()
        or "tee" in (c.type or "").lower()
        or "t-shirt" in (c.type or "").lower()
    ]
    totes = [
        c
        for c in clothes
        if "шоп" in (c.type or "").lower()
        or "tote" in (c.type or "").lower()
        or "сумк" in (c.type or "").lower()
        or "bag" in (c.type or "").lower()
    ]

    # Якщо однієї з категорій немає в БД, використовуємо наявні товари
    if not tshirts and clothes:
        tshirts = clothes[: max(1, len(clothes) // 2)]
    if not totes and clothes:
        totes = clothes[max(1, len(clothes) // 2) :] or clothes

    # Формуємо пари (tshirt, tote)
    pairs = []
    for tshirt in tshirts:
        for tote in totes:
            if tshirt.id != tote.id or len(clothes) == 1:
                pairs.append((tshirt, tote))

    if not pairs and clothes:
        pairs = [(clothes[0], clothes[0])]

    # Завжди гарантуємо РІВНО 6 пакетів
    selected_pairs = []
    idx = 0
    while len(selected_pairs) < MAX_PACKAGES_COUNT and pairs:
        selected_pairs.append((pairs[idx % len(pairs)], len(selected_pairs) + 1))
        idx += 1

    packages = []
    for (tshirt, tote), set_num in selected_pairs:
        total_price = float(tshirt.price + tote.price)
        discounted = round(total_price * (1 - SURVEY_DISCOUNT_PERCENT / 100), 2)
        packages.append(
            {
                "id": f"pkg_{tshirt.id}_{tote.id}_{set_num}",
                "tshirt": _serialize_item(tshirt),
                "tote": _serialize_item(tote),
                "price": total_price,
                "discountPercent": SURVEY_DISCOUNT_PERCENT,
                "discountedPrice": discounted,
            }
        )

    return packages


async def resolve_package_by_id(db: AsyncSession, package_id: str | None) -> dict | None:
    if not package_id:
        return None

    if package_id.startswith("pkg_"):
        parts = package_id.split("_")
        if len(parts) >= 3:
            try:
                tshirt_id = int(parts[1])
                tote_id = int(parts[2])
                tshirt = await crud_clothing.get_clothing_by_id(db, tshirt_id)
                tote = await crud_clothing.get_clothing_by_id(db, tote_id)
                if tshirt and tote:
                    total_price = float(tshirt.price + tote.price)
                    discounted = round(total_price * (1 - SURVEY_DISCOUNT_PERCENT / 100), 2)
                    return {
                        "id": package_id,
                        "tshirt": _serialize_item(tshirt),
                        "tote": _serialize_item(tote),
                        "price": total_price,
                        "discountPercent": SURVEY_DISCOUNT_PERCENT,
                        "discountedPrice": discounted,
                    }
            except ValueError:
                pass

    # Шукаємо у динамічно згенерованих пакетах
    dynamic_packages = await get_dynamic_packages(db)
    for p in dynamic_packages:
        if p["id"] == package_id:
            return p
    return None


async def get_random_package_id_from_db(db: AsyncSession) -> str | None:
    packages = await get_dynamic_packages(db)
    if packages:
        return random.choice(packages)["id"]
    return None
