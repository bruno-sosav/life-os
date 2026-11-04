from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.core.database.conexion_database import SessionDep
from app.modules.analytics.schemas.resumen_schema import AnalyticsSummary
from app.modules.analytics.services import resumen_service as service

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    today: date, session: SessionDep, week_offset: Annotated[int, Query(ge=0, le=520)] = 0
) -> AnalyticsSummary:
    """Todo lo de la pantalla Stats. `week_offset` mueve la semana del cumplimiento y el radar."""
    return service.get_summary(session, today, week_offset)
