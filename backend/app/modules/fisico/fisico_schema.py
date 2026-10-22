import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime

# Los decimales (kg, litros) viajan como número JSON, no como string.


# ─── Gym ────────────────────────────────────────────────────
class GymExerciseIn(BaseModel):
    exercise_name: str = Field(min_length=1, max_length=255)
    sets: int | None = Field(default=None, ge=0)
    reps: int | None = Field(default=None, ge=0)
    weight_kg: float | None = Field(default=None, ge=0, lt=10_000)
    notes: str | None = None


class GymExerciseOut(GymExerciseIn, ORMModel):
    id: str
    session_id: str


class GymSessionCreate(BaseModel):
    date: dt.date
    attended: bool = True
    routine_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    exercises: list[GymExerciseIn] = []


class GymSessionUpdate(BaseModel):
    date: dt.date | None = None
    attended: bool | None = None
    routine_name: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class GymSessionOut(ORMModel):
    id: str
    date: dt.date
    attended: bool
    routine_name: str | None
    notes: str | None
    created_at: UTCDateTime
    exercises: list[GymExerciseOut]


class ExerciseProgressionPoint(BaseModel):
    date: dt.date
    max_weight_kg: float | None
    volume_kg: float | None  # suma de series × reps × kg de esa sesión


# ─── MMA ────────────────────────────────────────────────────
class MmaSessionCreate(BaseModel):
    date: dt.date
    attended: bool = True
    session_type: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class MmaSessionUpdate(BaseModel):
    date: dt.date | None = None
    attended: bool | None = None
    session_type: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class MmaSessionOut(MmaSessionCreate, ORMModel):
    id: str
    attended: bool
    created_at: UTCDateTime


# ─── Peso / Nutrición ───────────────────────────────────────
class WeightLogIn(BaseModel):
    weight_kg: float = Field(gt=0, lt=1000)
    notes: str | None = None


class WeightLogOut(WeightLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime


class NutritionLogIn(BaseModel):
    quality_score: int | None = Field(default=None, ge=1, le=5)
    meals_count: int | None = Field(default=None, ge=0, le=20)
    water_liters: float | None = Field(default=None, ge=0, lt=100)
    notes: str | None = None


class NutritionLogOut(NutritionLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime
