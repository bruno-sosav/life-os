from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.rutina.models.habitos_model import Habit, HabitLog
from app.modules.rutina.repositories import habitos_repository
from app.modules.rutina.schemas.habitos_schema import HabitCreate, HabitLogUpsert, HabitUpdate


def list_habits(session: Session, active: bool | None) -> list[Habit]:
    return habitos_repository.list_habits(session, active)


def create_habit(session: Session, payload: HabitCreate) -> Habit:
    return base_repository.save(session, Habit(**payload.model_dump()))


def update_habit(session: Session, habit_id: str, payload: HabitUpdate) -> Habit:
    habit = get_or_404(session, Habit, habit_id)
    return base_repository.save(
        session, base_repository.apply(habit, payload.model_dump(exclude_unset=True))
    )


def delete_habit(session: Session, habit_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Habit, habit_id))


def completed_habit_logs(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    return habitos_repository.completed_habit_logs(session, start, end)


def upsert_habit_log(session: Session, payload: HabitLogUpsert) -> HabitLog:
    get_or_404(session, Habit, payload.habit_id)
    log = habitos_repository.habit_log_of(session, payload.habit_id, payload.date) or HabitLog(
        habit_id=payload.habit_id, date=payload.date
    )
    log.completed = payload.completed
    return base_repository.save(session, log)


def mark_linked_habit(session: Session, habit_id: str | None, day: date, done: bool) -> None:
    """Para los módulos que tienen un hábito vinculado (Físico, Mental): lo deja cumplido o no
    ese día. Un hábito borrado o pausado no se toca."""
    habit = session.get(Habit, habit_id) if habit_id else None
    if habit is None or not habit.active:
        return
    upsert_habit_log(session, HabitLogUpsert(habit_id=habit.id, date=day, completed=done))
