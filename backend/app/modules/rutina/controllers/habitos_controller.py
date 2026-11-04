from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.rutina.models.habitos_model import Habit, HabitLog
from app.modules.rutina.schemas.habitos_schema import (
    HabitCreate,
    HabitLogOut,
    HabitLogUpsert,
    HabitOut,
    HabitUpdate,
)
from app.modules.rutina.services import habitos_service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/habits", response_model=list[HabitOut])
def list_habits(session: SessionDep, active: bool | None = None) -> list[Habit]:
    """Lo usa Físico para elegir el hábito vinculado a una actividad."""
    return habitos_service.list_habits(session, active)


@router.post("/habits", response_model=HabitOut, status_code=CREATED)
def create_habit(payload: HabitCreate, session: SessionDep) -> Habit:
    return habitos_service.create_habit(session, payload)


@router.patch("/habits/{habit_id}", response_model=HabitOut)
def update_habit(habit_id: str, payload: HabitUpdate, session: SessionDep) -> Habit:
    return habitos_service.update_habit(session, habit_id, payload)


@router.delete("/habits/{habit_id}", status_code=NO_CONTENT)
def delete_habit(habit_id: str, session: SessionDep) -> Response:
    habitos_service.delete_habit(session, habit_id)
    return Response(status_code=NO_CONTENT)


@router.put("/habit-logs", response_model=HabitLogOut)
def upsert_habit_log(payload: HabitLogUpsert, session: SessionDep) -> HabitLog:
    return habitos_service.upsert_habit_log(session, payload)
