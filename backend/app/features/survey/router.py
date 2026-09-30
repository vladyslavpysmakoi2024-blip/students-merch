from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.features.survey.crud as crud_survey
from app.api.dependencies import get_current_user, get_db
from app.features.survey.schemas import (
    ClaimPackagePayload,
    ClaimPackageResponse,
    SurveyResponseSchema,
    SurveySubmit,
)
from app.features.survey.service import (
    get_dynamic_packages,
    get_random_package_id_from_db,
    resolve_package_by_id,
)
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


@router.get("/packages", response_model=list[dict])
async def get_survey_packages(db: AsyncSession = Depends(get_db)):
    return await get_dynamic_packages(db)


@router.get("/me", response_model=SurveyResponseSchema)
async def get_my_survey(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    survey = await crud_survey.get_survey_by_user(db, current_user.id)
    if not survey:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Survey is not completed")

    assigned_id = survey.assigned_package_id
    package_data = await resolve_package_by_id(db, assigned_id)

    if not assigned_id or not package_data:
        assigned_id = await get_random_package_id_from_db(db)
        if assigned_id:
            survey.assigned_package_id = assigned_id
            db.add(survey)
            await db.commit()
            await db.refresh(survey)
            package_data = await resolve_package_by_id(db, assigned_id)

    return SurveyResponseSchema(
        id=survey.id,
        id_user=survey.id_user,
        answers=survey.answers,
        completed_survey=current_user.completed_survey,
        assigned_package_id=assigned_id,
        is_package_confirmed=survey.is_package_confirmed,
        package=package_data,
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
    random_package_id = await get_random_package_id_from_db(db)
    survey = await crud_survey.create_survey(db, current_user, answers, assigned_package_id=random_package_id)

    package_data = await resolve_package_by_id(db, survey.assigned_package_id)

    return SurveyResponseSchema(
        id=survey.id,
        id_user=survey.id_user,
        answers=survey.answers,
        completed_survey=True,
        assigned_package_id=survey.assigned_package_id,
        is_package_confirmed=survey.is_package_confirmed,
        package=package_data,
        created_at=survey.created_at,
        updated_at=survey.updated_at,
    )


@router.post("/claim-package", response_model=ClaimPackageResponse)
async def claim_assigned_package(
    payload: ClaimPackagePayload | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    survey = await crud_survey.get_survey_by_user(db, current_user.id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Спочатку необхідно пройти опитування",
        )

    if not survey.is_package_confirmed:
        if payload and payload.package_id:
            survey.assigned_package_id = payload.package_id
        elif not survey.assigned_package_id:
            survey.assigned_package_id = await get_random_package_id_from_db(db)

        await crud_survey.confirm_package(db, survey)

    package_data = await resolve_package_by_id(db, survey.assigned_package_id)

    return ClaimPackageResponse(
        message="Сет успішно закріплено за вашим профілем",
        assigned_package_id=survey.assigned_package_id or "",
        is_package_confirmed=True,
        package=package_data,
    )
