"""Racha, agenda del día y cierre semanal. `today` lo manda el frontend: es su fecha local."""

from collections.abc import Iterable, Sequence
from datetime import date, timedelta
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.fechas_util import days_between, week_bounds
from app.core.numeros_util import js_round
from app.modules.dashboard import dashboard_repository as repository
from app.modules.dashboard.dashboard_schema import MoodLevel, StreakOut, WeeklyReviewSummary
from app.modules.fisico import GymSession, MmaSession
from app.modules.rutina import (
    STREAK_WINDOW_DAYS,
    Habit,
    RoutineBlock,
    block_completions,
    block_runs_on,
    completed_habit_logs,
    day_status,
    done_per_day,
    expected_per_day,
    habit_runs_on,
    list_habits,
    list_routine_blocks,
    streaks,
)
from app.modules.rutina import get_weekly_review as weekly_review_of
from app.modules.rutina.rutina_schema import WeeklyReviewOut


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
    return streaks(day_status(today, days, blocks, habits, done_dates))[0]


def habit_completion_pct(
    week_start: date, today: date, habits: Sequence[Habit], done_dates: Iterable[date]
) -> int | None:
    """% de hábitos cumplidos en la semana, contando solo hasta hoy. None si no tocaba ninguno."""
    week_end = min(week_start + timedelta(days=6), today)
    if week_end < week_start:
        return None
    days = pd.date_range(start=pd.Timestamp(week_start), end=pd.Timestamp(week_end), freq="D")
    expected = int(expected_per_day(days, [], habits).sum())
    done = int(done_per_day(days, done_dates).sum())
    return js_round(done / expected * 100) if expected else None


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
    days = days_between(week_bounds(today))
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
        if block_runs_on(block, day):
            entries.append((_start_minutes(block), _agenda_item(block, block.id in done_block_ids)))
    for habit in habits:
        if habit_runs_on(habit, day.weekday()):
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


# ─── Lo que piden los endpoints ─────────────────────────────
def get_streak(session: Session, today: date) -> StreakOut:
    start = today - timedelta(days=STREAK_WINDOW_DAYS - 1)
    done = [
        *(day for _, day in completed_habit_logs(session, start, today)),
        *(day for _, day in block_completions(session, start, today)),
    ]
    blocks = list_routine_blocks(session)
    habits = list_habits(session, active=True, linked_module=None)
    return StreakOut(streak=global_streak(today, blocks, habits, done))


def get_agenda(session: Session, day: date, today: date) -> dict[str, Any]:
    return agenda(
        day,
        today,
        list_routine_blocks(session),
        list_habits(session, active=True, linked_module=None),
        {block_id for block_id, _ in block_completions(session, day, day)},
        {habit_id for habit_id, _ in completed_habit_logs(session, day, day)},
    )


def get_weekly_review(session: Session, today: date) -> WeeklyReviewSummary:
    """Cierre de la semana de `today` (lunes a domingo) comparado con la anterior."""
    week_start, week_end = week_bounds(today)
    prev_start = week_bounds(today, 1).start
    habits = list_habits(session, active=True, linked_module=None)
    done = [day for _, day in completed_habit_logs(session, prev_start, week_end)]

    habit_pct = habit_completion_pct(week_start, today, habits, done) or 0
    prev_habit_pct = habit_completion_pct(prev_start, today, habits, done)
    avg = repository.avg_mood(session, week_start, week_end)
    avg_mood = round(avg, 2) if avg is not None else None
    review = weekly_review_of(session, week_start)
    return WeeklyReviewSummary(
        week_start=week_start,
        week_end=week_end,
        habit_pct=habit_pct,
        prev_habit_pct=prev_habit_pct or 0,
        # Una semana anterior al 0 % también se compara; solo se omite si no tocaba nada
        habit_pct_delta=None if prev_habit_pct is None else habit_pct - prev_habit_pct,
        gym_days=repository.attended_days(session, GymSession, week_start, week_end),
        mma_days=repository.attended_days(session, MmaSession, week_start, week_end),
        avg_mood=avg_mood,
        mood_level=mood_level(avg_mood),
        review=WeeklyReviewOut.model_validate(review) if review else None,
    )
