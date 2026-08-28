from __future__ import annotations
from typing import TYPE_CHECKING # ignoring this in runtime

from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column, String, LargeBinary
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.models import Favorite, Order, Bin


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    password: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    fathers_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    street: Mapped[str | None] = mapped_column(Text, nullable=True)
    house_number: Mapped[str | None] = mapped_column(Text, nullable=True)

    favorites: Mapped[list[Favorite]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders: Mapped[list[Order]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    bin: Mapped[list[Bin]] = relationship(
        "Bin",
        back_populates="user",
        cascade="all, delete-orphan"
    )

