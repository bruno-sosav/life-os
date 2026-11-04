from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.mood_model import MoodLog
from app.modules.mental.schemas.mood_schema import MoodAverage, MoodLogIn, MoodLogOut
from app.modules.mental.services import mood_service

router = APIRouter()


@router.get("/mood-logs", response_model=list[MoodLogOut])
def list_mood_logs(session: SessionDep, start: date | None = None) -> list[MoodLog]:
    return mood_service.list_mood_logs(session, start)


@router.get("/mood-logs/average", response_model=MoodAverage)
def mood_average(today: date, session: SessionDep) -> MoodAverage:
    return mood_service.mood_average(session, today)


@router.put("/mood-logs/{day}", response_model=MoodLogOut)
def upsert_mood_log(day: date, payload: MoodLogIn, session: SessionDep) -> MoodLog:
    return mood_service.upsert_mood_log(session, day, payload)
