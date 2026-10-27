from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.modules.rutina.rutina_schema import HabitOut, RoutineBlockOut, WeeklyReviewOut


class StreakOut(BaseModel):
    streak: int


MoodLevel = Literal["excelente", "buena", "regular", "dificil"]
AgendaSection = Literal["manana", "tarde", "noche", "sin_horario"]


class WeeklyReviewSummary(BaseModel):
    week_start: date
    week_end: date
    habit_pct: int
    prev_habit_pct: int
    habit_pct_delta: int | None  # None si la semana anterior no tenía hábitos agendados
    gym_days: int
    mma_days: int
    avg_mood: float | None
    mood_level: MoodLevel | None
    review: WeeklyReviewOut | None


class WeekDay(BaseModel):
    date: date
    weekday: int  # 0 = lunes
    is_today: bool


class AgendaItem(BaseModel):
    kind: Literal["block", "habit"]
    id: str
    title: str
    emoji: str | None
    color: str | None
    category: str | None
    time: str | None  # "HH:MM"
    done: bool
    block: RoutineBlockOut | None = None  # registro completo, para editar
    habit: HabitOut | None = None


class AgendaSectionOut(BaseModel):
    key: AgendaSection
    label: str
    items: list[AgendaItem]


class AgendaOut(BaseModel):
    date: date
    weekday: int
    week: list[WeekDay]
    sections: list[AgendaSectionOut]
    completed: int
    total: int
    pct: int
