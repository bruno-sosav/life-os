"""Cálculos del dashboard (racha y cierre semanal) sobre los registros ya leídos de la base."""

import math
from collections.abc import Iterable, Sequence
from datetime import date, timedelta
from typing import Any

import pandas as pd

from app.models import Habit, RoutineBlock
from app.schemas.rutina import MoodLevel

STREAK_WINDOW_DAYS = 60
STREAK_THRESHOLD = 0.7  # un día cuenta si se completó al menos el 70 % de lo esperado


def js_round(value: float) -> int:
    """Redondeo como Math.round de JS (2.5 → 3), igual que los cálculos originales del frontend."""
    return math.floor(value + 0.5)


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
    return js_round(done / expected * 100) if expected else 0


# ─── Agenda del día ─────────────────────────────────────────
SECTIONS = (  # (clave, título, minuto desde, minuto hasta)
    ("manana", "Mañana", 0, 12 * 60),
    ("tarde", "Tarde", 12 * 60, 20 * 60),
    ("noche", "Noche", 20 * 60, 24 * 60),
)


def _start_minutes(item: RoutineBlock | Habit) -> int | None:
    if isinstance(item, RoutineBlock):
        return item.hour_start * 60 + (item.hour_min or 0)
    if item.start_time is None:
        return None
    return item.start_time.hour * 60 + item.start_time.minute


def week_days(today: date) -> list[dict[str, Any]]:
    monday = today - timedelta(days=today.weekday())
    days = (monday + timedelta(days=i) for i in range(7))
    return [{"date": d, "weekday": d.weekday(), "is_today": d == today} for d in days]


def agenda(
    day: date,
    today: date,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done_block_ids: set[str],
    done_habit_ids: set[str],
) -> dict[str, Any]:
    """Bloques y hábitos de `day`, ordenados por hora y agrupados por momento del día."""
    entries: list[tuple[int | None, dict[str, Any]]] = []
    for block in blocks:
        if _block_runs_on(block, day):
            entries.append((_start_minutes(block), _agenda_item(block, block.id in done_block_ids)))
    for habit in habits:
        if _habit_runs_on(habit, day.weekday()):
            entries.append((_start_minutes(habit), _agenda_item(habit, habit.id in done_habit_ids)))
    # Primero los que tienen hora (por hora); al final los sin horario. Orden estable.
    entries.sort(key=lambda e: (e[0] is None, e[0] or 0))

    sections = [
        {
            "key": key,
            "label": label,
            "items": [it for m, it in entries if m is not None and lo <= m < hi],
        }
        for key, label, lo, hi in SECTIONS
    ]
    sections.append(
        {
            "key": "sin_horario",
            "label": "Sin horario",
            "items": [it for m, it in entries if m is None],
        }
    )
    total = len(entries)
    completed = sum(1 for _, it in entries if it["done"])
    return {
        "date": day,
        "weekday": day.weekday(),
        "week": week_days(today),
        "sections": [s for s in sections if s["items"]],
        "completed": completed,
        "total": total,
        "pct": js_round(completed / total * 100) if total else 0,
    }


def _agenda_item(item: RoutineBlock | Habit, done: bool) -> dict[str, Any]:
    minutes = _start_minutes(item)
    fields: dict[str, Any] = {
        "id": item.id,
        "emoji": item.emoji,
        "color": item.color,
        "time": None if minutes is None else f"{minutes // 60:02d}:{minutes % 60:02d}",
        "done": done,
    }
    if isinstance(item, RoutineBlock):
        return {
            **fields,
            "kind": "block",
            "title": item.activity,
            "category": item.category,
            "block": item,
        }
    return {**fields, "kind": "habit", "title": item.name, "category": None, "habit": item}


# ─── Cierre semanal ─────────────────────────────────────────
def mood_level(avg: float | None) -> MoodLevel | None:
    if not avg:
        return None
    if avg >= 4.5:
        return "excelente"
    if avg >= 3.5:
        return "buena"
    if avg >= 2.5:
        return "regular"
    return "dificil"
