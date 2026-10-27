from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query

from app.core.database.conexion_database import SessionDep
from app.modules.analytics import analytics_service as service
from app.modules.analytics.analytics_schema import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(
    today: date, session: SessionDep, week_offset: Annotated[int, Query(ge=0, le=520)] = 0
) -> AnalyticsSummary:
    """Todo lo de la pantalla Stats, calculado. `week_offset` mueve la semana del Score/radar."""
    return service.get_summary(session, today, week_offset)
