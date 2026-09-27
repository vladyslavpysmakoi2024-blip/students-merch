from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.features.user.models import User


class SurveyResponse(Base):
    __tablename__ = "survey_response"
    __table_args__ = (UniqueConstraint("id_user", name="uq_survey_response_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    answers: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    user: Mapped[User] = relationship("User", back_populates="survey_response")
