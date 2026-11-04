from datetime import date, time
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime

DayOfWeek = Annotated[int, Field(ge=0, le=6)]  # 0 = lunes … 6 = domingo


def _all_or_some_days(days: list[int] | None) -> list[int] | None:
    """Días únicos y ordenados; ninguno o los 7 equivale a todos los días (None)."""
    if days is None:
        return None
    unique = sorted(set(days))
    return None if len(unique) in (0, 7) else unique


HabitDays = Annotated[list[DayOfWeek] | None, AfterValidator(_all_or_some_days)]


class HabitBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    color: str | None = "#30D158"
    emoji: str | None = None
    start_time: time | None = None
    duration_min: int | None = Field(default=30, ge=0, le=1440)
    days_of_week: HabitDays = None  # null = todos los días
    sort_order: int = 0


class HabitCreate(HabitBase):
    active: bool = True


class HabitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    color: str | None = None
    emoji: str | None = None
    active: bool | None = None
    start_time: time | None = None
    duration_min: int | None = Field(default=None, ge=0, le=1440)
    days_of_week: HabitDays = None
    sort_order: int | None = None


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
    created_at: UTCDateTime
