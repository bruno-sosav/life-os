import datetime as dt

from pydantic import BaseModel

from app.modules.rutina import DayStatus


# ─── Resumen calculado (GET /analytics/summary) ─────────────
class Compliance(BaseModel):
    """Cuánto de lo agendado (hábitos y bloques) se hizo en la semana, hasta hoy."""

    pct: int | None  # None si no había nada agendado
    done: int
    expected: int
    prev_pct: int | None  # semana anterior
    delta: int | None  # pct - prev_pct, si las dos semanas tienen datos


class CompliancePoint(BaseModel):
    week_start: dt.date
    pct: int | None
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


class ActivityCount(BaseModel):
    id: str
    name: str
    emoji: str | None
    color: str | None
    count: int  # días con la actividad en los últimos 30 días


class FinanceMonth(BaseModel):
    month: dt.date
    income: int
    expenses: int
    savings_pct: int | None


class AnalyticsSummary(BaseModel):
    week_start: dt.date
    week_end: dt.date
    compliance: Compliance
    compliance_history: list[CompliancePoint]
    kpis: KPIs
    habits_by_week: HabitsByWeek
    radar: list[RadarAxis]
    heatmap: Heatmap
    weight_series: list[WeightPoint]
    mood_series: list[MoodPoint]
    activity_distribution: list[ActivityCount]
    finance_monthly: list[FinanceMonth]
