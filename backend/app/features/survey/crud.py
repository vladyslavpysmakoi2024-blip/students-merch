from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.survey.models import SurveyResponse
from app.features.user.models import User


async def get_survey_by_user(db: AsyncSession, user_id: int) -> SurveyResponse | None:
    query = select(SurveyResponse).where(SurveyResponse.id_user == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def create_survey(
    db: AsyncSession, user: User, answers: list[dict], assigned_package_id: str | None = None
) -> SurveyResponse:
    survey = SurveyResponse(
        id_user=user.id,
        answers=answers,
        assigned_package_id=assigned_package_id,
        is_package_confirmed=False,
    )
    db.add(survey)
    user.completed_survey = True
    db.add(user)
    await db.commit()
    await db.refresh(survey)
    await db.refresh(user)
    return survey


async def confirm_package(db: AsyncSession, survey: SurveyResponse) -> SurveyResponse:
    survey.is_package_confirmed = True
    db.add(survey)
    await db.commit()
    await db.refresh(survey)
    return survey
