import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime

TaskStatus = Literal["pendiente", "en_progreso", "hecho"]
TaskPriority = Literal["alta", "media", "baja"]


# ─── Proyectos ──────────────────────────────────────────────
class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    color: str | None = "#0A84FF"
    emoji: str | None = "📁"
    description: str | None = None


class ProjectOut(ProjectIn, ORMModel):
    id: str
    created_at: UTCDateTime


# ─── Tareas ─────────────────────────────────────────────────
class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus = "pendiente"
    priority: TaskPriority = "media"
    project_id: str | None = None
    due_date: dt.date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    project_id: str | None = None
    due_date: dt.date | None = None


class TaskOut(TaskIn, ORMModel):
    id: str
    completed_at: UTCDateTime | None
    created_at: UTCDateTime


# ─── Ideas ──────────────────────────────────────────────────
class BusinessIdeaIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str | None = None
    tags: list[str] | None = None


class BusinessIdeaOut(BusinessIdeaIn, ORMModel):
    id: str
    created_at: UTCDateTime


# ─── Objetivos del mes ──────────────────────────────────────
class GoalIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    month: dt.date  # cualquier día del mes; se guarda como el día 1


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    progress: int | None = Field(default=None, ge=0, le=100)


class GoalOut(ORMModel):
    id: str
    title: str
    month: dt.date
    progress: int
    completed: bool
    created_at: UTCDateTime
