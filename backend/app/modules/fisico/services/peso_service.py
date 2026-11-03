from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.modules.fisico.models.peso_model import WeightGoal, WeightLog
from app.modules.fisico.repositories import (
    peso_repository,
)
from app.modules.fisico.schemas.peso_schema import WeightGoalIn, WeightLogIn


def list_weight_logs(session: Session, start: date | None) -> list[WeightLog]:
    return peso_repository.list_weight_logs(session, start)


def upsert_weight_log(session: Session, day: date, payload: WeightLogIn) -> WeightLog:
    log = peso_repository.weight_log_of(session, day) or WeightLog(date=day)
    return base_repository.save(session, base_repository.apply(log, payload.model_dump()))


def get_weight_goal(session: Session) -> WeightGoalIn:
    goal = peso_repository.weight_goal(session)
    return WeightGoalIn(weight_kg=goal.weight_kg if goal else None)


def set_weight_goal(session: Session, payload: WeightGoalIn) -> WeightGoalIn:
    goal = peso_repository.weight_goal(session) or WeightGoal()
    base_repository.save(session, base_repository.apply(goal, payload.model_dump()))
    return payload
