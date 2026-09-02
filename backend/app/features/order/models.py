from __future__ import annotations
from typing import TYPE_CHECKING # ignoring this in runtime
from decimal import Decimal

from sqlalchemy import (
    Integer, Text, ForeignKey, DateTime, DECIMAL, VARCHAR
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.user.models import User
    from app.features.order_content.models import OrderContent

class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    delivery_company: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_number: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    date: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    user: Mapped[User] = relationship("User", back_populates="orders")

    order_content: Mapped[list[OrderContent]] = relationship(
        "OrderContent",
        back_populates="order",
        cascade="all, delete-orphan"
    )
