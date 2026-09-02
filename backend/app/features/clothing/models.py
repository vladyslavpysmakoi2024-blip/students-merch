from __future__ import annotations
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import (
    Integer, Text, ARRAY, DECIMAL, VARCHAR
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
if TYPE_CHECKING:
    from app.features.favorite.models import Favorite
    from app.features.order_content.models import OrderContent
    from app.features.cart.models import Cart


class Clothing(Base):
    __tablename__ = "clothing"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(VARCHAR(7), nullable=True) # Збереження HEX-кольорів
    size: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    composition: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photos: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)

    favorites: Mapped[list[Favorite]] = relationship(
        "Favorite",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )
    order_content: Mapped[list[OrderContent]] = relationship(
        "OrderContent",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )

    cart: Mapped[list[Cart]] = relationship(
        "Cart",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )
