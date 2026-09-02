from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.user.models import User
    from app.features.clothing.models import Clothing


class Favorite(Base):
    __tablename__ = "favorite"

    __table_args__ = (
        UniqueConstraint(
            "id_user",
            "id_clothing",
            name="uq_favorite_user_clothing"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    id_clothing: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("clothing.id"),
        nullable=False
    )

    id_user: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    clothing: Mapped[Clothing] = relationship(
        "Clothing",
        back_populates="favorites"
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="favorites"
    )