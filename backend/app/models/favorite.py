from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from app.models.user import User

import app.models

class Favorite(Base):
    __tablename__ = "favorite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_clothing: Mapped[int | None] = mapped_column(Integer, ForeignKey("clothing.id"), nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    clothing: Mapped["Clothing"] = relationship("Clothing", back_populates="favorites")
    user: Mapped["User"] = relationship("User", back_populates="favorites")
