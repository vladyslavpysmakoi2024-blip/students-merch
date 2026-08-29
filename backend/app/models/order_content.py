from typing import TYPE_CHECKING # ignoring this in runtime

from sqlalchemy import (
    Integer, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.models import Clothing, Order

class OrderContent(Base):
    __tablename__ = "order_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_clothing: Mapped[int | None] = mapped_column(Integer, ForeignKey("clothing.id"), nullable=True)
    id_order: Mapped[int | None] = mapped_column(Integer, ForeignKey("order.id"), nullable=True)

    clothing: Mapped[Clothing] = relationship("Clothing", back_populates="order_content")
    order: Mapped[Order] = relationship("Order", back_populates="order_content")
