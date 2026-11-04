from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.dashboard.schemas.racha_schema import StreakOut
from app.modules.dashboard.services import racha_service

router = APIRouter()


@router.get("/streak", response_model=StreakOut)
def get_streak(today: date, session: SessionDep) -> StreakOut:
    return racha_service.get_streak(session, today)
