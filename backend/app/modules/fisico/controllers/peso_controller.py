from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.fisico.models.peso_model import WeightLog
from app.modules.fisico.schemas.peso_schema import WeightGoalIn, WeightLogIn, WeightLogOut
from app.modules.fisico.services import peso_service as service

router = APIRouter()


@router.get("/weight-logs", response_model=list[WeightLogOut])
def list_weight_logs(session: SessionDep, start: date | None = None) -> list[WeightLog]:
    return service.list_weight_logs(session, start)


@router.put("/weight-logs/{day}", response_model=WeightLogOut)
def upsert_weight_log(day: date, payload: WeightLogIn, session: SessionDep) -> WeightLog:
    return service.upsert_weight_log(session, day, payload)


@router.get("/weight-goal", response_model=WeightGoalIn)
def get_weight_goal(session: SessionDep) -> WeightGoalIn:
    return service.get_weight_goal(session)


@router.put("/weight-goal", response_model=WeightGoalIn)
def set_weight_goal(payload: WeightGoalIn, session: SessionDep) -> WeightGoalIn:
    return service.set_weight_goal(session, payload)
