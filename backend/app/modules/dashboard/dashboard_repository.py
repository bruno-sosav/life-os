"""Dashboard no tiene tablas propias. Lo de rutina lo pide a rutina; acá lee físico y mental."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.fisico import GymSession, MmaSession
from app.modules.mental import MoodLog


def attended_days(
    session: Session, model: type[GymSession | MmaSession], start: date, end: date
) -> int:
    query = (
        select(func.count(func.distinct(model.date)))
        .where(model.attended.is_(True))
        .where(model.date.between(start, end))
    )
    return session.scalar(query) or 0


def avg_mood(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None
