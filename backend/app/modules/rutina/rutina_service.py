from collections.abc import Iterable, Sequence
from datetime import date
from typing import Literal

import pandas as pd
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


# ─── Qué toca cada día (lo usan dashboard y analytics) ──────
STREAK_THRESHOLD = 0.7  # un día se cumple con al menos el 70 % de lo agendado
STREAK_WINDOW_DAYS = 90  # la racha y el mapa de Stats miran estos días hacia atrás

DayStatus = Literal["cumplido", "parcial", "sin_cumplir", "libre", "pendiente"]


def _exists_on(record: Habit | RoutineBlock, day: date) -> bool:
    """Lo creado después de `day` no cuenta ese día: sumar un hábito no baja el pasado."""
    return record.created_at is None or record.created_at.date() <= day


def habit_runs_on(habit: Habit, dow: int) -> bool:
    return not habit.days_of_week or dow in habit.days_of_week


def block_runs_on(block: RoutineBlock, day: date) -> bool:
    if not block.repeat_weekly:
        return block.specific_date == day
    if block.days_of_week:
        return day.weekday() in block.days_of_week
    return block.day_of_week == day.weekday()


def expected_per_day(
    days: pd.DatetimeIndex, blocks: Sequence[RoutineBlock], habits: Sequence[Habit]
) -> pd.Series:
    """Cantidad de bloques + hábitos agendados para cada día.

    Los semanales cuentan desde que se crearon; un bloque de fecha puntual cuenta siempre.
    """
    values = [
        sum(block_runs_on(b, day) and (not b.repeat_weekly or _exists_on(b, day)) for b in blocks)
        + sum(habit_runs_on(h, day.weekday()) and _exists_on(h, day) for h in habits)
        for day in (d.date() for d in days)
    ]
    return pd.Series(values, index=days, dtype="int64")


def done_per_day(days: pd.DatetimeIndex, done_dates: Iterable[date]) -> pd.Series:
    counts = pd.Series(pd.to_datetime(list(done_dates)), dtype="datetime64[ns]").value_counts()
    return counts.reindex(days, fill_value=0).astype("int64")


def day_status(
    today: date,
    days: pd.DatetimeIndex,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done_dates: Iterable[date],
) -> pd.Series:
    """Estado de cada día con la regla del 70 %. Hoy, si todavía no llegó, queda 'pendiente'."""
    expected = expected_per_day(days, blocks, habits)
    done = done_per_day(days, done_dates)
    ratio = done / expected.where(expected > 0)
    status = pd.Series("sin_cumplir", index=days, dtype="object")
    status[done > 0] = "parcial"
    status[ratio >= STREAK_THRESHOLD] = "cumplido"
    status[expected == 0] = "libre"
    status[(status.index == pd.Timestamp(today)) & (status != "cumplido") & (status != "libre")] = (
        "pendiente"
    )
    return status


def streaks(status: pd.Series) -> tuple[int, int]:
    """(racha actual, mejor racha) de días cumplidos seguidos. Libres y hoy pendiente no cortan."""
    ok = status[~status.isin(["libre", "pendiente"])] == "cumplido"
    if ok.empty:
        return 0, 0
    runs = ok.groupby((~ok).cumsum()).cumsum()  # largo de la racha que termina en cada día
    return int(runs.iloc[-1]), int(runs.max())
