import datetime as dt

from pydantic import BaseModel


class TrainingDay(BaseModel):
    date: dt.date
    activity_ids: list[str]  # qué tipos entrenaste ese día (sesión o hábito vinculado)


class TrainingDays(BaseModel):
    count: int  # días entrenados en el rango
    days: list[TrainingDay]
