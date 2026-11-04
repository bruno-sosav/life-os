from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mental.models.mood_model import MoodLog


def list_mood_logs(session: Session, start: date | None) -> list[MoodLog]:
    query = select(MoodLog).order_by(MoodLog.date)
    if start is not None:
        query = query.where(MoodLog.date >= start)
    return list(session.scalars(query))


def avg_mood(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None


def mood_log_of(session: Session, day: date) -> MoodLog | None:
    return session.scalar(select(MoodLog).where(MoodLog.date == day))
