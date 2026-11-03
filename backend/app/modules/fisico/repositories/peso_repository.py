from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.fisico.models.peso_model import WeightGoal, WeightLog


def list_weight_logs(session: Session, start: date | None) -> list[WeightLog]:
    query = select(WeightLog).order_by(WeightLog.date)
    if start is not None:
        query = query.where(WeightLog.date >= start)
    return list(session.scalars(query))


def weight_log_of(session: Session, day: date) -> WeightLog | None:
    return session.scalar(select(WeightLog).where(WeightLog.date == day))


def weight_goal(session: Session) -> WeightGoal | None:
    return session.scalar(select(WeightGoal).limit(1))
