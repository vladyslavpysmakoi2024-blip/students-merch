from typing import TYPE_CHECKING

from sqlalchemy import (
    Integer, ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.user.models import User
    from app.features.clothing.models import Clothing

class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Прибрали | None та nullable=True, оскільки в БД стоїть Not NULL
    id_clothing: Mapped[int] = mapped_column(Integer, ForeignKey("clothing.id"))
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    clothing: Mapped[Clothing] = relationship("Clothing", back_populates="cart")
    user: Mapped[User] = relationship("User", back_populates="cart")
