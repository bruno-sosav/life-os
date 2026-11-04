from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.dashboard.schemas.cierre_schema import WeeklyReviewSummary
from app.modules.dashboard.services import cierre_service

router = APIRouter()


@router.get("/weekly-review", response_model=WeeklyReviewSummary)
def get_weekly_review(today: date, session: SessionDep) -> WeeklyReviewSummary:
    return cierre_service.get_weekly_review(session, today)
