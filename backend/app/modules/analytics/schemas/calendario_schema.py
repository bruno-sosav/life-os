import datetime as dt

from pydantic import BaseModel

from app.modules.rutina import DayStatus


class CalendarDay(BaseModel):
    date: dt.date
    status: DayStatus  # misma regla del 70 % que la racha; hoy y los días que vienen: pendiente
    done: int
    expected: int
    pct: int | None  # None si no había nada agendado


class CalendarWeek(BaseModel):
    week_start: dt.date  # lunes
    pct: int | None  # % de la semana entera hasta hoy; None si no había nada o no llegó


class CalendarMonth(BaseModel):
    days: list[CalendarDay]
    weeks: list[CalendarWeek]  # las semanas que tocan el mes, lunes a domingo
    # Días del mes en cada estado (los libres y los pendientes no se cuentan)
    cumplido: int
    parcial: int
    sin_cumplir: int
