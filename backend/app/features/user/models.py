from __future__ import annotations

from typing import TYPE_CHECKING  # ignoring this in runtime

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.cart.models import Cart
    from app.features.favorite.models import Favorite
    from app.features.order.models import Order
    from app.features.survey.models import SurveyResponse


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
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_survey: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    favorites: Mapped[list[Favorite]] = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

    orders: Mapped[list[Order]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")

    cart: Mapped[list[Cart]] = relationship("Cart", back_populates="user", cascade="all, delete-orphan")

    survey_response: Mapped[SurveyResponse | None] = relationship(
        "SurveyResponse", back_populates="user", cascade="all, delete-orphan", uselist=False
    )
