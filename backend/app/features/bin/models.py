from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.user.models import User
    from app.features.clothing.models import Clothing

class Bin(Base):
    __tablename__ = "bin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    id_clothing: Mapped[int | None] = mapped_column(Integer, ForeignKey("clothing.id"), nullable=True)
    id_user: Mapped[int | None] = mapped_column(Integer, ForeignKey("user.id"), nullable=True)

    clothing: Mapped[Clothing] = relationship("Clothing", back_populates="bin")
    user: Mapped[User] = relationship("User", back_populates="bin")
