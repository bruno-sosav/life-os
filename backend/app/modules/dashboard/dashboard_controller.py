from datetime import date
from typing import Any

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.dashboard import dashboard_service as service
from app.modules.dashboard.dashboard_schema import AgendaOut, StreakOut, WeeklyReviewSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/streak", response_model=StreakOut)
def get_streak(today: date, session: SessionDep) -> StreakOut:
    return service.get_streak(session, today)


@router.get("/agenda", response_model=AgendaOut)
def get_agenda(date: date, today: date, session: SessionDep) -> dict[str, Any]:
    """Agenda de `date`: secciones con bloques y hábitos ordenados, y el progreso del día."""
    return service.get_agenda(session, date, today)


@router.get("/weekly-review", response_model=WeeklyReviewSummary)
def get_weekly_review(today: date, session: SessionDep) -> WeeklyReviewSummary:
    return service.get_weekly_review(session, today)
