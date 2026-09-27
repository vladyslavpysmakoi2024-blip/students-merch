from __future__ import annotations

from typing import TYPE_CHECKING  # ignoring this in runtime

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.clothing.models import Clothing
    from app.features.order.models import Order


class OrderContent(Base):
    __tablename__ = "order_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_clothing: Mapped[int | None] = mapped_column(Integer, ForeignKey("clothing.id"), nullable=True)
    id_order: Mapped[int | None] = mapped_column(Integer, ForeignKey("order.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    clothing: Mapped[Clothing] = relationship("Clothing", back_populates="order_content")
    order: Mapped[Order] = relationship("Order", back_populates="order_content")
