import datetime as dt

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, Score, UTCDateTime


class MoodLogIn(BaseModel):
    mood_score: int | None = Score
    energy_score: int | None = Score
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    notes: str | None = None


class MoodLogOut(MoodLogIn, ORMModel):
    id: str
    date: dt.date
    created_at: UTCDateTime


class MoodAverage(BaseModel):
    avg_mood: float | None  # promedio de los últimos 7 días, o None sin registros
