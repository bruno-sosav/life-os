import datetime as dt
from typing import Any

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class ExerciseIn(BaseModel):
    exercise_name: str = Field(min_length=1, max_length=255)
    sets: int | None = Field(default=None, ge=0)
    reps: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, lt=10_000)
    notes: str | None = None


class ExerciseOut(ExerciseIn, ORMModel):
    id: str
    session_id: str


class SessionIn(BaseModel):
    activity_id: str
    date: dt.date
    attended: bool = True
    notes: str | None = None
    values: dict[str, Any] = {}  # {field_id: valor}; se valida contra los campos de la actividad
    exercises: list[ExerciseIn] = []


class SessionOut(ORMModel):
    id: str
    activity_id: str
    date: dt.date
    attended: bool
    notes: str | None
    values: dict[str, Any]
    exercises: list[ExerciseOut]
    created_at: UTCDateTime


class ProgressionPoint(BaseModel):
    date: dt.date
    value: float | None  # carga máxima del ejercicio, o el valor del campo ese día


class ExerciseProgression(BaseModel):
    points: list[ProgressionPoint]
    best: ProgressionPoint | None  # el récord: la carga más alta (la primera vez que se logró)


class LastExercise(BaseModel):
    """Lo que hiciste de un ejercicio la última vez, para tenerlo a mano al cargar."""

    date: dt.date
    activity_id: str
    sets: list[ExerciseIn]
