from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column, String, Float, ARRAY
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
import app.models

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
    photos: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)


    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )
    order_content: Mapped[list["OrderContent"]] = relationship(
        "OrderContent",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )

    bin: Mapped[list["Bin"]] = relationship(
        "Bin",
        back_populates="clothing",
        cascade="all, delete-orphan"
    )
