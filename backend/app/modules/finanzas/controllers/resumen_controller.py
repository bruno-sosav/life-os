from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.finanzas.schemas.resumen_schema import Labels, MonthSummary
from app.modules.finanzas.services import resumen_service

router = APIRouter()


@router.get("/summary", response_model=MonthSummary)
def month_summary(month: date, session: SessionDep) -> MonthSummary:
    """Totales, ahorro y gasto por categoría del mes que contiene `month`."""
    return resumen_service.month_summary(session, month)


@router.get("/labels", response_model=Labels)
def labels(session: SessionDep) -> Labels:
    return resumen_service.labels(session)
