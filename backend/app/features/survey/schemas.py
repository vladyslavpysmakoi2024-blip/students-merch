from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SurveyAnswerItem(BaseModel):
    id: str
    title: str
    type: str
    value: str | list[str]


class SurveySubmit(BaseModel):
    answers: list[SurveyAnswerItem] = Field(min_length=1)


class SurveyResponseSchema(BaseModel):
    id: int
    id_user: int
    answers: list[dict[str, Any]]
    completed_survey: bool = True
    assigned_package_id: str | None = None
    is_package_confirmed: bool = False
    package: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimPackagePayload(BaseModel):
    package_id: str | None = None


class ClaimPackageResponse(BaseModel):
    message: str
    assigned_package_id: str
    is_package_confirmed: bool = True
    package: dict[str, Any] | None = None
