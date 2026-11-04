from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.rutina.models.revisiones_model import WeeklyReview
from app.modules.rutina.schemas.revisiones_schema import WeeklyReviewIn, WeeklyReviewOut
from app.modules.rutina.services import revisiones_service

router = APIRouter()


@router.put("/weekly-reviews/{week_start}", response_model=WeeklyReviewOut)
def upsert_weekly_review(
    week_start: date, payload: WeeklyReviewIn, session: SessionDep
) -> WeeklyReview:
    return revisiones_service.upsert_weekly_review(session, week_start, payload)
