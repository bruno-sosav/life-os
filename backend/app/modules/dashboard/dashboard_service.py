"""Racha, agenda del día y cierre semanal. `today` lo manda el frontend: es su fecha local."""

from collections.abc import Iterable, Sequence
from datetime import date, timedelta
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.core.fechas_util import days_between, week_bounds
from app.core.numeros_util import js_round
from app.modules.dashboard.dashboard_schema import (
    ActivityDays,
    MoodLevel,
    StreakOut,
    WeeklyReviewSummary,
)
from app.modules.fisico import Activity, attended_days, list_activities
from app.modules.mental import avg_mood
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
    scheduled_on,
    streaks,
)
from app.modules.rutina import get_weekly_review as weekly_review_of
from app.modules.rutina.rutina_schema import WeeklyReviewOut


def global_streak(
    today: date,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done: Iterable[tuple[str, date]],
) -> int:
    """Días seguidos (hacia atrás desde hoy) con al menos el 70 % de la agenda cumplida.

    Los días sin nada agendado no cortan ni suman. Hoy suma si ya llegó al umbral;
    si todavía no, no corta la racha porque el día no terminó.
    """
    days = pd.date_range(end=pd.Timestamp(today), periods=STREAK_WINDOW_DAYS, freq="D")
    return streaks(day_status(today, days, blocks, habits, done))[0]


def habit_completion_pct(
    week_start: date, today: date, habits: Sequence[Habit], done: Iterable[tuple[str, date]]
) -> int | None:
    """% de hábitos cumplidos en la semana, contando solo hasta hoy. None si no tocaba ninguno."""
    week_end = min(week_start + timedelta(days=6), today)
    if week_end < week_start:
        return None
    days = pd.date_range(start=pd.Timestamp(week_start), end=pd.Timestamp(week_end), freq="D")
    expected = int(expected_per_day(days, [], habits).sum())
    did = int(done_per_day(days, [], habits, done).sum())
    return js_round(did / expected * 100) if expected else None


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


def _on_agenda(item: RoutineBlock | Habit, day: date, today: date) -> bool:
    if day < today:
        return scheduled_on(item, day)
    if isinstance(item, RoutineBlock):
        return block_runs_on(item, day)
    return habit_runs_on(item, day.weekday())


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
    """Bloques y hábitos de `day`, ordenados por hora y agrupados por momento del día.

    Un día pasado muestra lo que estaba agendado entonces (lo mismo que cuenta la racha).
    Hoy y los días futuros muestran todo, también lo recién creado.
    """
    done_ids = done_block_ids | done_habit_ids
    entries: list[tuple[int | None, dict[str, Any]]] = []
    items: list[RoutineBlock | Habit] = [*blocks, *habits]
    for item in items:
        if _on_agenda(item, day, today):
            entries.append((_start_minutes(item), _agenda_item(item, item.id in done_ids)))
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


def activity_days(
    activities: Sequence[Activity], attended: Iterable[tuple[str, date]]
) -> list[ActivityDays]:
    """Días con sesión por actividad. Las pausadas solo aparecen si igual se usaron."""
    days: dict[str, set[date]] = {}
    for activity_id, day in attended:
        days.setdefault(activity_id, set()).add(day)
    return [
        ActivityDays(
            id=a.id, name=a.name, emoji=a.emoji, color=a.color, days=len(days.get(a.id, ()))
        )
        for a in activities
        if a.active or a.id in days
    ]


# ─── Lo que piden los endpoints ─────────────────────────────
def get_streak(session: Session, today: date) -> StreakOut:
    start = today - timedelta(days=STREAK_WINDOW_DAYS - 1)
    done = [
        *completed_habit_logs(session, start, today),
        *block_completions(session, start, today),
    ]
    blocks = list_routine_blocks(session)
    habits = list_habits(session, active=True)
    return StreakOut(streak=global_streak(today, blocks, habits, done))


def get_agenda(session: Session, day: date, today: date) -> dict[str, Any]:
    return agenda(
        day,
        today,
        list_routine_blocks(session),
        list_habits(session, active=True),
        {block_id for block_id, _ in block_completions(session, day, day)},
        {habit_id for habit_id, _ in completed_habit_logs(session, day, day)},
    )


def get_weekly_review(session: Session, today: date) -> WeeklyReviewSummary:
    """Cierre de la semana de `today` (lunes a domingo) comparado con la anterior."""
    week_start, week_end = week_bounds(today)
    prev_start = week_bounds(today, 1).start
    habits = list_habits(session, active=True)
    done = completed_habit_logs(session, prev_start, week_end)

    habit_pct = habit_completion_pct(week_start, today, habits, done) or 0
    prev_habit_pct = habit_completion_pct(prev_start, today, habits, done)
    avg = avg_mood(session, week_start, week_end)
    mood = round(avg, 2) if avg is not None else None
    review = weekly_review_of(session, week_start)
    return WeeklyReviewSummary(
        week_start=week_start,
        week_end=week_end,
        habit_pct=habit_pct,
        prev_habit_pct=prev_habit_pct or 0,
        # Una semana anterior al 0 % también se compara; solo se omite si no tocaba nada
        habit_pct_delta=None if prev_habit_pct is None else habit_pct - prev_habit_pct,
        activity_days=activity_days(
            list_activities(session), attended_days(session, week_start, week_end)
        ),
        avg_mood=mood,
        mood_level=mood_level(mood),
        review=WeeklyReviewOut.model_validate(review) if review else None,
    )
