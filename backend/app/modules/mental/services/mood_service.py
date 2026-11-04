from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.modules.mental.models.mood_model import MoodLog
from app.modules.mental.repositories import mood_repository
from app.modules.mental.schemas.mood_schema import MoodAverage, MoodLogIn


def list_mood_logs(session: Session, start: date | None) -> list[MoodLog]:
    return mood_repository.list_mood_logs(session, start)


def avg_mood(session: Session, start: date, end: date) -> float | None:
    return mood_repository.avg_mood(session, start, end)


def mood_average(session: Session, today: date) -> MoodAverage:
    avg = avg_mood(session, today - timedelta(days=6), today)
    return MoodAverage(avg_mood=round(avg, 1) if avg is not None else None)


def upsert_mood_log(session: Session, day: date, payload: MoodLogIn) -> MoodLog:
    log = mood_repository.mood_log_of(session, day) or MoodLog(date=day)
    return base_repository.save(session, base_repository.apply(log, payload.model_dump()))
