from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models import User, Clothing

class Bin(Base):
    __tablename__ = "bin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_clothing: Mapped[int | None] = mapped_column(Integer, ForeignKey("clothing.id"), nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    clothing: Mapped[Clothing] = relationship("Clothing", back_populates="bin")
    user: Mapped[User] = relationship("User", back_populates="bin")
