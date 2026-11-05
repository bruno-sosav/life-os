import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from app.core.base_schema import Label, UTCDateTime
from app.modules.mental.schemas.recursos_schema import ResourceOut

# Las etapas quedan fijas: ordenan la lista y "practicando" es lo que mide la meta
SkillStage = Literal["practicando", "en_pausa", "la_tengo"]
WeeklyGoal = Field(default=None, ge=1, le=7 * 24 * 60)  # minutos por semana


class SkillIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: Label | None = None
    stage: SkillStage = "practicando"
    weekly_goal_min: int | None = WeeklyGoal
    habit_id: str | None = None


class SkillUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: Label | None = None
    stage: SkillStage | None = None
    weekly_goal_min: int | None = WeeklyGoal
    habit_id: str | None = None


class SkillCreated(SkillIn):
    """Lo que vuelve al crear o editar: los datos guardados (lo calculado sale de GET /skills)."""

    id: str


class WeekMinutes(BaseModel):
    week_start: dt.date  # lunes
    minutes: int


class BookRef(BaseModel):
    id: str
    title: str
    status: str


class SkillOut(BaseModel):
    """La skill con lo que llevás, ya calculado."""

    id: str
    name: str
    type: str | None
    stage: SkillStage
    weekly_goal_min: int | None
    habit_id: str | None
    week_minutes: int  # en la semana de `today`
    total_minutes: int
    last_practice: dt.date | None
    weeks: list[WeekMinutes]  # las últimas 6 semanas, de la más vieja a la actual
    resources: list[ResourceOut]
    books: list[BookRef]
    created_at: UTCDateTime
