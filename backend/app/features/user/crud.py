from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.features.user.models import User
from app.features.user.schemas import UserCreate, UserUpdate


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    # 1. Хешуємо пароль перед збереженням
    hashed_password = hash_password(user_in.password)

    # 2. Витягуємо дані зі схеми UserCreate
    new_user = User(
        email=user_in.email,
        password=hashed_password,  # <--- ВИПРАВЛЕНО ТУТ
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        phone_number=user_in.phone_number,
    )

    # 3. Зберігаємо в БД
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def create_user_google(
    db: AsyncSession, email: str, first_name: str, last_name: str
) -> User:
    new_user = User(
        email=email, first_name=first_name, last_name=last_name, password=None
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_user(db: AsyncSession, db_user: User, user_in: UserUpdate) -> User:
    # Отримуємо лише ті поля, які були передані в запиті (exclude_unset=True)
    # user_in може містити city, street, house_number, fathers_name тощо
    update_data = user_in.model_dump(exclude_unset=True)

    # Динамічно оновлюємо атрибути моделі бази даних
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_password(db: AsyncSession, db_user: User, new_password: str) -> User:
    db_user.password = hash_password(new_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
