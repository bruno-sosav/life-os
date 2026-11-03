import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


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
