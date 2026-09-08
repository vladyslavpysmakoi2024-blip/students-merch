from sqlalchemy.ext.asyncio import AsyncSession

from app.features.auth.schemas import UserGoogleCreate
from app.features.user.models import User


async def create_user_google(db: AsyncSession, user_in: UserGoogleCreate):
    new_user = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
