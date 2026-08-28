from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column, String, LargeBinary, Float, ARRAY
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
if TYPE_CHECKING:
    from app.models import Favorite, OrderContent, Bin

class Clothing(Base):
    __tablename__ = "clothing"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str | None] = mapped_column(Text, nullable=True)
    color: Mapped[str | None] = mapped_column(Text, nullable=True)
    size: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str | None] = mapped_column(Text, nullable=True)
    composition: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    photo: Mapped[list[bytes] | None] = mapped_column(ARRAY(LargeBinary), nullable=True)


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

    bin: Mapped[list[Bin]] = relationship(
        "Bin",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )
