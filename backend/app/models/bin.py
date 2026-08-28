from sqlalchemy import (
    Integer, Text, Boolean, ForeignKey, Column
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
import app.models

class Bin(Base):
    __tablename__ = "bin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_clothing: Mapped[int | None] = mapped_column(Integer, ForeignKey("clothing.id"), nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    clothing: Mapped["Clothing"] = relationship("Clothing", back_populates="bin")
    user: Mapped["User"] = relationship("User", back_populates="bin")
