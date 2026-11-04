import datetime as dt

from pydantic import BaseModel


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
