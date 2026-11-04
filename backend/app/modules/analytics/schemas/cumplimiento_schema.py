import datetime as dt

from pydantic import BaseModel

from app.modules.rutina import DayStatus


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


class HeatCell(BaseModel):
    date: dt.date | None  # None = celda de relleno de la grilla
    status: DayStatus | None


class Heatmap(BaseModel):
    cells: list[HeatCell]
    # Días de cada estado en los 90 días (los libres y hoy pendiente no se cuentan)
    cumplido: int
    parcial: int
    sin_cumplir: int
