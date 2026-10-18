"""Cálculos del dashboard (racha y cierre semanal) sobre los registros ya leídos de la base."""

from collections.abc import Iterable, Sequence
from datetime import date, timedelta

import pandas as pd

from app.models import Habit, RoutineBlock

STREAK_WINDOW_DAYS = 60
STREAK_THRESHOLD = 0.7  # un día cuenta si se completó al menos el 70 % de lo esperado


def _habit_runs_on(habit: Habit, dow: int) -> bool:
    return not habit.days_of_week or dow in habit.days_of_week


def _block_runs_on(block: RoutineBlock, day: date) -> bool:
    if not block.repeat_weekly:
        return block.specific_date == day
    if block.days_of_week:
        return day.weekday() in block.days_of_week
    return block.day_of_week == day.weekday()


def expected_per_day(
    days: pd.DatetimeIndex, blocks: Sequence[RoutineBlock], habits: Sequence[Habit]
) -> pd.Series:
    """Cantidad de bloques + hábitos agendados para cada día."""
    values = [
        sum(_block_runs_on(b, d.date()) for b in blocks)
        + sum(_habit_runs_on(h, d.weekday()) for h in habits)
        for d in days
    ]
    return pd.Series(values, index=days, dtype="int64")


def done_per_day(days: pd.DatetimeIndex, done_dates: Iterable[date]) -> pd.Series:
    counts = pd.Series(pd.to_datetime(list(done_dates)), dtype="datetime64[ns]").value_counts()
    return counts.reindex(days, fill_value=0).astype("int64")


def global_streak(
    today: date,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done_dates: Iterable[date],
) -> int:
    """Días seguidos (hacia atrás desde hoy) con al menos el 70 % de la agenda cumplida.

    Los días sin nada agendado no cortan ni suman. Hoy suma si ya llegó al umbral;
    si todavía no, no corta la racha porque el día no terminó.
    """
    days = pd.date_range(end=pd.Timestamp(today), periods=STREAK_WINDOW_DAYS, freq="D")
    df = pd.DataFrame(
        {"expected": expected_per_day(days, blocks, habits), "done": done_per_day(days, done_dates)}
    )
    df = df[df["expected"] > 0].sort_index(ascending=False)
    ok = (df["done"] / df["expected"]) >= STREAK_THRESHOLD

    if not ok.empty and ok.index[0].date() == today and not ok.iloc[0]:
        ok = ok.iloc[1:]
    # cantidad de True consecutivos al principio
    return int(ok.astype("int64").cumprod().sum())


def habit_completion_pct(
    week_start: date, today: date, habits: Sequence[Habit], done_dates: Iterable[date]
) -> int:
    """% de hábitos cumplidos en la semana, contando solo hasta hoy."""
    week_end = min(week_start + timedelta(days=6), today)
    if week_end < week_start:
        return 0
    days = pd.date_range(start=pd.Timestamp(week_start), end=pd.Timestamp(week_end), freq="D")
    expected = int(expected_per_day(days, [], habits).sum())
    done = int(done_per_day(days, done_dates).sum())
    return round(done / expected * 100) if expected else 0
