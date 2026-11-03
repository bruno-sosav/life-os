import datetime as dt
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, model_validator

from app.core.base_schema import ORMModel, UTCDateTime
from app.core.database.base_model import new_uuid

# Los decimales (kg, litros) viajan como número JSON, no como string.

# Las piezas con las que se arma el formulario de cualquier actividad
FieldType = Literal["numero", "texto", "si_no", "opcion", "escala", "ejercicios"]
CHARTABLE: tuple[FieldType, ...] = ("numero", "escala")  # se pueden graficar en el tiempo


# ─── Actividades ────────────────────────────────────────────
class ActivityField(BaseModel):
    # El id no cambia nunca: los valores de las sesiones se guardan por id, no por nombre
    id: str = Field(default_factory=new_uuid, min_length=1, max_length=36)
    name: str = Field(min_length=1, max_length=60)
    type: FieldType
    unit: str | None = Field(default=None, max_length=20)  # "km", "min"…
    options: list[str] | None = None  # solo para "opcion"
    archived: bool = False  # archivado: no se carga más, pero el historial se sigue viendo

    @model_validator(mode="after")
    def check_options(self) -> Self:
        if self.type == "opcion":
            self.options = list(dict.fromkeys(o.strip() for o in self.options or [] if o.strip()))
            if not self.options:
                raise ValueError(f"El campo '{self.name}' necesita al menos una opción")
        else:
            self.options = None
        return self


def _check_fields(fields: list[ActivityField] | None) -> None:
    if fields is None:
        return
    if len({f.id for f in fields}) != len(fields):
        raise ValueError("Hay campos con el mismo id")
    if sum(f.type == "ejercicios" and not f.archived for f in fields) > 1:
        raise ValueError("Una actividad tiene como mucho una lista de ejercicios")


class ActivityIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    emoji: str | None = Field(default=None, max_length=32)
    color: str | None = "#0A84FF"
    active: bool = True
    sort_order: int = 0
    fields: list[ActivityField] = []
    habit_id: str | None = None

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        _check_fields(self.fields)
        return self


class ActivityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    emoji: str | None = Field(default=None, max_length=32)
    color: str | None = None
    active: bool | None = None
    sort_order: int | None = None
    # Lista completa. Un campo que ya no viene queda archivado, no se borra.
    fields: list[ActivityField] | None = None
    habit_id: str | None = None

    @model_validator(mode="after")
    def check_fields(self) -> Self:
        _check_fields(self.fields)
        return self


class ActivityOut(ORMModel):
    id: str
    name: str
    emoji: str | None
    color: str | None
    active: bool
    sort_order: int
    fields: list[ActivityField]
    habit_id: str | None
    created_at: UTCDateTime


# ─── Sesiones ───────────────────────────────────────────────
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


# ─── Asistencia y calendario ────────────────────────────────
class LinkedHabitOut(ORMModel):
    id: str
    name: str


class AttendanceDay(BaseModel):
    date: dt.date
    attended: bool


class AttendanceWeek(BaseModel):
    habit: LinkedHabitOut | None  # con hábito vinculado, la asistencia sale de sus registros
    days: list[AttendanceDay]  # lunes a domingo


class MonthDay(BaseModel):
    date: dt.date
    attended: bool | None  # False = sesión sin asistir; None = nada ese día


class ActivityMonth(BaseModel):
    count: int  # días asistidos en el mes
    days: list[MonthDay]


# ─── Peso / Nutrición ───────────────────────────────────────
class WeightLogIn(BaseModel):
    weight_kg: float = Field(gt=0, lt=1000)
    notes: str | None = None


class WeightLogOut(WeightLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime


class WeightGoalIn(BaseModel):
    weight_kg: float | None = Field(gt=0, lt=1000)  # None = sin meta


class NutritionLogIn(BaseModel):
    quality_score: int | None = Field(default=None, ge=1, le=5)
    meals_count: int | None = Field(default=None, ge=0, le=20)
    water_liters: float | None = Field(default=None, ge=0, lt=100)
    notes: str | None = None


class NutritionLogOut(NutritionLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime


class NutritionAverage(BaseModel):
    avg_quality: float | None  # promedio de calidad de los últimos 7 días
