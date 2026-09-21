from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, VARCHAR, DateTime, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.order_content.models import OrderContent
    from app.features.user.models import User


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    delivery_company: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_number: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    date: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    status: Mapped[str] = mapped_column(
        Enum("created", "processing", "paid", "failure", name="orderstatus"),
        default="created",
        nullable=False,
    )
    user: Mapped[User] = relationship("User", back_populates="orders")
    invoice_id: Mapped[str | None] = mapped_column(Text, nullable=True)

    order_content: Mapped[list[OrderContent]] = relationship(
        "OrderContent", back_populates="order", cascade="all, delete-orphan"
    )
