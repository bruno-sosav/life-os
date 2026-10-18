from datetime import date, time
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, UTCDateTime

DayOfWeek = Annotated[int, Field(ge=0, le=6)]  # 0 = lunes … 6 = domingo
LinkedModule = Literal["gym", "mma"]


# ─── Hábitos ────────────────────────────────────────────────
class HabitBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    color: str | None = "#30D158"
    icon: str | None = None
    emoji: str | None = None
    start_time: time | None = None
    duration_min: int | None = Field(default=30, ge=0, le=1440)
    days_of_week: list[DayOfWeek] | None = None  # null = todos los días
    sort_order: int = 0
    linked_module: LinkedModule | None = None


class HabitCreate(HabitBase):
    active: bool = True


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    color: str | None = None
    icon: str | None = None
    emoji: str | None = None
    active: bool | None = None
    start_time: time | None = None
    duration_min: int | None = Field(default=None, ge=0, le=1440)
    days_of_week: list[DayOfWeek] | None = None
    sort_order: int | None = None
    linked_module: LinkedModule | None = None


class HabitOut(HabitBase, ORMModel):
    id: str
    active: bool
    created_at: UTCDateTime


class HabitLogUpsert(BaseModel):
    habit_id: str
    date: date
    completed: bool


class HabitLogOut(ORMModel):
    id: str
    habit_id: str
    date: date
    completed: bool
    note: str | None
    created_at: UTCDateTime


# ─── Rutina ─────────────────────────────────────────────────
class RoutineBlockIn(BaseModel):
    day_of_week: DayOfWeek | None = None
    days_of_week: list[DayOfWeek] | None = None
    specific_date: date | None = None
    repeat_weekly: bool = True
    hour_start: int = Field(ge=0, le=23)
    hour_min: int = Field(default=0, ge=0, le=59)
    hour_end: int = Field(ge=0, le=23)
    activity: str = Field(min_length=1, max_length=255)
    category: str | None = None
    emoji: str | None = None
    color: str | None = None


class RoutineBlockOut(RoutineBlockIn, ORMModel):
    id: str


class RoutineCompletionToggle(BaseModel):
    block_id: str
    date: date
    completed: bool


class RoutineCompletionOut(ORMModel):
    id: str
    block_id: str
    date: date
    completed: bool
    completed_at: UTCDateTime


# ─── Cierre semanal ─────────────────────────────────────────
class WeeklyReviewIn(BaseModel):
    went_well: str | None = None
    would_change: str | None = None


class WeeklyReviewOut(WeeklyReviewIn, ORMModel):
    id: str
    week_start: date
    created_at: UTCDateTime


# ─── Estadísticas ───────────────────────────────────────────
class StreakOut(BaseModel):
    streak: int


class WeeklyStatsOut(BaseModel):
    habit_pct: int
    prev_habit_pct: int
    gym_days: int
    mma_days: int
    avg_mood: float | None
