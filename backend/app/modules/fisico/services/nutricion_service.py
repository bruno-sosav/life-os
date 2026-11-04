from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.modules.fisico.models.nutricion_model import NutritionLog
from app.modules.fisico.repositories import nutricion_repository
from app.modules.fisico.schemas.nutricion_schema import NutritionAverage, NutritionLogIn


def list_nutrition_logs(session: Session, start: date | None) -> list[NutritionLog]:
    return nutricion_repository.list_nutrition_logs(session, start)


def nutrition_average(session: Session, today: date) -> NutritionAverage:
    avg = nutricion_repository.avg_nutrition_quality(session, today - timedelta(days=6), today)
    return NutritionAverage(avg_quality=round(avg, 1) if avg is not None else None)


def upsert_nutrition_log(session: Session, day: date, payload: NutritionLogIn) -> NutritionLog:
    log = nutricion_repository.nutrition_log_of(session, day) or NutritionLog(date=day)
    return base_repository.save(session, base_repository.apply(log, payload.model_dump()))
