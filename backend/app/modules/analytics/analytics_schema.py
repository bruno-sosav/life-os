import datetime as dt
from typing import Literal

from pydantic import BaseModel

from app.modules.rutina import DayStatus


# ─── Resumen calculado (GET /analytics/summary) ─────────────
class BruceScore(BaseModel):
    total: int
    level: Literal["elite", "modo_bruce", "activando", "apagado"]
    habit_score: int
    workout_score: int
    stratus_score: int
    completed_habits: int
    expected_habits: int
    workouts: int
    stratus_days: int


class BrucePoint(BaseModel):
    week_start: dt.date
    score: int
    is_current: bool


class KPIs(BaseModel):
    current_streak: int
    best_streak: int
    workouts_month: int
    habit_month_pct: int
    last_weight: float | None
    weight_trend: float | None  # kg contra el último registro de hace 30+ días
    year: int
    books_year: int


class HabitRef(BaseModel):
    id: str
    name: str
    color: str | None


class HabitsByWeek(BaseModel):
    habits: list[HabitRef]
    # Una fila por semana: {"week_start": "...", "<habit_id>": completados, ...}
    weeks: list[dict[str, int | str]]


class RadarAxis(BaseModel):
    axis: str
    semana: int
    anterior: int


class HeatCell(BaseModel):
    date: dt.date | None  # None = celda de relleno de la grilla
    status: DayStatus | None


class Heatmap(BaseModel):
    cells: list[HeatCell]
    # Días de cada estado en los 90 días (los libres y hoy pendiente no se cuentan)
    cumplido: int
    parcial: int
    sin_cumplir: int


class WeightPoint(BaseModel):
    date: dt.date
    kg: float


class MoodPoint(BaseModel):
    date: dt.date
    mood: int | None
    sleep: float | None


class GymVsMma(BaseModel):
    gym: int
    mma: int


class FinanceMonth(BaseModel):
    month: dt.date
    income: int
    expenses: int
    savings_pct: int | None


class AnalyticsSummary(BaseModel):
    week_start: dt.date
    week_end: dt.date
    bruce: BruceScore
    bruce_history: list[BrucePoint]
    kpis: KPIs
    habits_by_week: HabitsByWeek
    radar: list[RadarAxis]
    heatmap: Heatmap
    weight_series: list[WeightPoint]
    mood_series: list[MoodPoint]
    gym_vs_mma: GymVsMma
    finance_monthly: list[FinanceMonth]
