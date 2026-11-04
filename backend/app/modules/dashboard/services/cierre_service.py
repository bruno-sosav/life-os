from collections.abc import Iterable, Sequence
from datetime import date, timedelta

import pandas as pd
from sqlalchemy.orm import Session

from app.core.fechas_util import week_bounds
from app.core.numeros_util import js_round
from app.modules.dashboard.schemas.cierre_schema import ActivityDays, MoodLevel, WeeklyReviewSummary
from app.modules.fisico import Activity, attended_days, list_activities
from app.modules.mental import avg_mood
from app.modules.rutina import (
    Habit,
    WeeklyReviewOut,
    completed_habit_logs,
    done_per_day,
    expected_per_day,
    list_habits,
)
from app.modules.rutina import get_weekly_review as weekly_review_of


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
