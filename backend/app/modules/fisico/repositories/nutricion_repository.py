from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.fisico.models.nutricion_model import NutritionLog


def list_nutrition_logs(session: Session, start: date | None) -> list[NutritionLog]:
    query = select(NutritionLog).order_by(NutritionLog.date)
    if start is not None:
        query = query.where(NutritionLog.date >= start)
    return list(session.scalars(query))


def avg_nutrition_quality(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(NutritionLog.quality_score)).where(NutritionLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None


def nutrition_log_of(session: Session, day: date) -> NutritionLog | None:
    return session.scalar(select(NutritionLog).where(NutritionLog.date == day))
