from datetime import date
from typing import Literal

from pydantic import BaseModel

from app.modules.rutina import HabitOut, RoutineBlockOut

AgendaSection = Literal["manana", "tarde", "noche", "sin_horario"]


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
