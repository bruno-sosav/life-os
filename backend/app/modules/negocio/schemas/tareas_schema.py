import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime

TaskStatus = Literal["pendiente", "en_progreso", "hecho"]
TaskPriority = Literal["alta", "media", "baja"]


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = "pendiente"
    priority: TaskPriority = "media"
    project_id: str
    due_date: dt.date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    project_id: str | None = None  # pasarla a otro proyecto; no puede quedar sin proyecto
    due_date: dt.date | None = None


class TaskMove(BaseModel):
    """Arrastrar en el tablero: a qué columna y en qué lugar (0 = arriba de todo)."""

    status: TaskStatus
    position: int = Field(ge=0)


class TaskOut(TaskIn, ORMModel):
    id: str
    position: int
    completed_at: UTCDateTime | None
    created_at: UTCDateTime


Board = dict[TaskStatus, list[TaskOut]]
