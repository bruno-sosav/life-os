from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.negocio.models.objetivos_model import StratusGoal


def list_goals(session: Session, month: date) -> list[StratusGoal]:
    query = select(StratusGoal).where(StratusGoal.month == month).order_by(StratusGoal.created_at)
    return list(session.scalars(query))
