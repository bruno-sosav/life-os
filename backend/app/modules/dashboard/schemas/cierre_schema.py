from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.modules.rutina import WeeklyReviewOut

MoodLevel = Literal["excelente", "buena", "regular", "dificil"]


class ActivityDays(BaseModel):
    id: str
    name: str
    emoji: str | None
    color: str | None
    days: int  # días distintos con sesión asistida en la semana


class WeeklyReviewSummary(BaseModel):
    week_start: date
    week_end: date
    habit_pct: int
    prev_habit_pct: int
    habit_pct_delta: int | None  # None si la semana anterior no tenía hábitos agendados
    # Actividades activas y las pausadas que igual tuvieron sesiones esa semana
    activity_days: list[ActivityDays]
    avg_mood: float | None
    mood_level: MoodLevel | None
    review: WeeklyReviewOut | None
