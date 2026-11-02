"""Dashboard no tiene tablas propias. Rutina y físico le pasan lo suyo; acá lee el mood."""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mental import MoodLog


def avg_mood(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(MoodLog.mood_score)).where(MoodLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None
