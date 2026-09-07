from datetime import date
from decimal import Decimal

from sqlalchemy import Integer, String, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Promo(Base):
    __tablename__ = "promo"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    promo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    date_start: Mapped[date] = mapped_column(Date, nullable=False)

    date_end: Mapped[date] = mapped_column(Date, nullable=False)

    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
