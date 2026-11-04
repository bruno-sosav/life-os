from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.analytics.schemas.calendario_schema import CalendarMonth
from app.modules.analytics.services import calendario_service as service

router = APIRouter()


@router.get("/calendar", response_model=CalendarMonth)
def month_calendar(month: date, today: date, session: SessionDep) -> CalendarMonth:
    """El mes que contiene `month`, día por día. `today` es la fecha local del frontend."""
    return service.month_calendar(session, month, today)
