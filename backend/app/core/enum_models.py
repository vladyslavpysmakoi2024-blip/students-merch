from __future__ import annotations

# from typing import TYPE_CHECKING, Any
from sqlalchemy import VARCHAR, Identity, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.database import Base


class EnumStatus(Base):
    __tablename__ = "enum_status"

    id: Mapped[int] = mapped_column(SmallInteger, Identity(), primary_key=True)
    data: Mapped[str] = mapped_column(VARCHAR(14), nullable=False)

    @validates("data")
    def validate_data(self, key: str, value: str) -> str:
        if value is not None:
            return value.upper()
        return value
