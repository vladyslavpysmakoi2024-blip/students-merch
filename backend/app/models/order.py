from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column, String, LargeBinary, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
import app.models

class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cost: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_company: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivery_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    date: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")

    order_content: Mapped[list["OrderContent"]] = relationship(
        "OrderContent",
        back_populates="order",
        cascade="all, delete-orphan"
    )
