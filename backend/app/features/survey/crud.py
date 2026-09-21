from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.features.survey.models import SurveyResponse
from app.features.user.models import User


async def get_survey_by_user(db: AsyncSession, user_id: int) -> SurveyResponse | None:
    query = select(SurveyResponse).where(SurveyResponse.id_user == user_id)
    result = await db.execute(query)
    return result.scalars().first()


async def upsert_survey(db: AsyncSession, user: User, answers: list[dict]) -> SurveyResponse:
    survey = await get_survey_by_user(db, user.id)

    if survey:
        survey.answers = answers
        flag_modified(survey, "answers")
    else:
        survey = SurveyResponse(id_user=user.id, answers=answers)
        db.add(survey)

    user.completed_survey = True
    db.add(user)
    await db.commit()
    await db.refresh(survey)
    await db.refresh(user)
    return survey
