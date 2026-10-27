from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.rutina import rutina_repository as repository
from app.modules.rutina.rutina_model import (
    Habit,
    HabitLog,
    RoutineBlock,
    RoutineCompletion,
    WeeklyReview,
)
from app.modules.rutina.rutina_schema import (
    HabitCreate,
    HabitLogUpsert,
    HabitUpdate,
    RoutineBlockIn,
    RoutineCompletionToggle,
    WeeklyReviewIn,
)


# ─── Hábitos ────────────────────────────────────────────────
def list_habits(session: Session, active: bool | None, linked_module: str | None) -> list[Habit]:
    return repository.list_habits(session, active, linked_module)


def create_habit(session: Session, payload: HabitCreate) -> Habit:
    return base_repository.save(session, Habit(**payload.model_dump()))


def update_habit(session: Session, habit_id: str, payload: HabitUpdate) -> Habit:
    habit = get_or_404(session, Habit, habit_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    return base_repository.save(session, habit)


def delete_habit(session: Session, habit_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Habit, habit_id))


# ─── Logs de hábitos (uno por hábito y día) ─────────────────
def list_habit_logs(session: Session, start: date, end: date) -> list[HabitLog]:
    return repository.list_habit_logs(session, start, end)


def upsert_habit_log(session: Session, payload: HabitLogUpsert) -> HabitLog:
    get_or_404(session, Habit, payload.habit_id)
    log = repository.habit_log_of(session, payload.habit_id, payload.date) or HabitLog(
        habit_id=payload.habit_id, date=payload.date
    )
    log.completed = payload.completed
    return base_repository.save(session, log)


# ─── Bloques de rutina ──────────────────────────────────────
def list_routine_blocks(session: Session) -> list[RoutineBlock]:
    return repository.list_routine_blocks(session)


def create_routine_block(session: Session, payload: RoutineBlockIn) -> RoutineBlock:
    return base_repository.save(session, RoutineBlock(**payload.model_dump()))


def replace_routine_block(session: Session, block_id: str, payload: RoutineBlockIn) -> RoutineBlock:
    block = get_or_404(session, RoutineBlock, block_id)
    for field, value in payload.model_dump().items():
        setattr(block, field, value)
    return base_repository.save(session, block)


def delete_routine_block(session: Session, block_id: str) -> None:
    base_repository.delete(session, get_or_404(session, RoutineBlock, block_id))


# ─── Completions de rutina ──────────────────────────────────
def list_routine_completions(session: Session, day: date) -> list[RoutineCompletion]:
    return repository.list_routine_completions(session, day)


def toggle_routine_completion(session: Session, payload: RoutineCompletionToggle) -> None:
    """completed=true la registra; completed=false la borra."""
    get_or_404(session, RoutineBlock, payload.block_id)
    completion = repository.completion_of(session, payload.block_id, payload.date)
    if payload.completed and completion is None:
        base_repository.save(
            session, RoutineCompletion(block_id=payload.block_id, date=payload.date)
        )
    elif not payload.completed and completion is not None:
        base_repository.delete(session, completion)


# ─── Cierre semanal (uno por semana) ────────────────────────
def get_weekly_review(session: Session, week_start: date) -> WeeklyReview | None:
    return repository.weekly_review_of(session, week_start)


def upsert_weekly_review(
    session: Session, week_start: date, payload: WeeklyReviewIn
) -> WeeklyReview:
    review = repository.weekly_review_of(session, week_start) or WeeklyReview(week_start=week_start)
    review.went_well = payload.went_well
    review.would_change = payload.would_change
    return base_repository.save(session, review)
