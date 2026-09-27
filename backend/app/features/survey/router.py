from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.survey.crud as crud_survey
from app.api.dependencies import get_current_user, get_db
from app.features.survey.schemas import SurveyResponseSchema, SurveySubmit
from app.features.user.models import User

router = APIRouter(prefix="/survey", tags=["Survey"])

REQUIRED_QUESTION_IDS = {
    "color",
    "season",
    "childhood",
    "milk",
    "logo",
    "drinks",
    "daytime",
    "tea",
    "tabs",
    "alarms",
    "transport",
}


def _validate_answers(payload: SurveySubmit) -> list[dict]:
    seen: set[str] = set()
    serialized: list[dict] = []

    for item in payload.answers:
        if item.id in seen:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Duplicate question: {item.id}")
        seen.add(item.id)

        value = item.value
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Empty answer: {item.id}")
        elif isinstance(value, list):
            value = [option.strip() for option in value if option.strip()]
            if not value:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Empty answer: {item.id}")
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid answer: {item.id}")

        serialized.append({"id": item.id, "title": item.title, "type": item.type, "value": value})

    missing = REQUIRED_QUESTION_IDS - seen
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing answers: {', '.join(sorted(missing))}",
        )

    return serialized


@router.get("/me", response_model=SurveyResponseSchema)
async def get_my_survey(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    survey = await crud_survey.get_survey_by_user(db, current_user.id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey is not completed")
    return SurveyResponseSchema(
        id=survey.id,
        id_user=survey.id_user,
        answers=survey.answers,
        completed_survey=current_user.completed_survey,
        created_at=survey.created_at,
        updated_at=survey.updated_at,
    )


@router.post("/me", response_model=SurveyResponseSchema)
async def submit_survey(
    payload: SurveySubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = await crud_survey.get_survey_by_user(db, current_user.id)
    if current_user.completed_survey or existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Survey is already completed",
        )

    answers = _validate_answers(payload)
    survey = await crud_survey.create_survey(db, current_user, answers)
    return SurveyResponseSchema(
        id=survey.id,
        id_user=survey.id_user,
        answers=survey.answers,
        completed_survey=True,
        created_at=survey.created_at,
        updated_at=survey.updated_at,
    )
