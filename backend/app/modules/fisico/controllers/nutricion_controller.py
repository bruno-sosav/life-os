from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.fisico.models.nutricion_model import NutritionLog
from app.modules.fisico.schemas.nutricion_schema import (
    NutritionAverage,
    NutritionLogIn,
    NutritionLogOut,
)
from app.modules.fisico.services import nutricion_service as service

router = APIRouter()


@router.get("/nutrition-logs", response_model=list[NutritionLogOut])
def list_nutrition_logs(session: SessionDep, start: date | None = None) -> list[NutritionLog]:
    return service.list_nutrition_logs(session, start)


@router.get("/nutrition-logs/average", response_model=NutritionAverage)
def nutrition_average(today: date, session: SessionDep) -> NutritionAverage:
    return service.nutrition_average(session, today)


@router.put("/nutrition-logs/{day}", response_model=NutritionLogOut)
def upsert_nutrition_log(day: date, payload: NutritionLogIn, session: SessionDep) -> NutritionLog:
    return service.upsert_nutrition_log(session, day, payload)
