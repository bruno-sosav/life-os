from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.fisico.schemas.asistencia_schema import TrainingDays
from app.modules.fisico.services import asistencia_service as service

router = APIRouter()


@router.get("/training/week", response_model=TrainingDays)
def training_week(today: date, session: SessionDep) -> TrainingDays:
    return service.training_week(session, today)


@router.get("/training/month", response_model=TrainingDays)
def training_month(month: date, session: SessionDep) -> TrainingDays:
    return service.training_month(session, month)
