"""Semanas (lunes a domingo) y meses, calculados igual en todos los módulos."""

import calendar
from datetime import date, timedelta
from typing import NamedTuple


class Period(NamedTuple):
    start: date
    end: date


def week_bounds(day: date, offset: int = 0) -> Period:
    """Semana de lunes a domingo que contiene `day`, `offset` semanas hacia atrás."""
    monday = day - timedelta(days=day.weekday() + 7 * offset)
    return Period(monday, monday + timedelta(days=6))


def month_bounds(day: date) -> Period:
    """Primer y último día del mes de `day`."""
    last = calendar.monthrange(day.year, day.month)[1]
    return Period(day.replace(day=1), day.replace(day=last))


def days_between(period: Period) -> list[date]:
    return [period.start + timedelta(days=i) for i in range((period.end - period.start).days + 1)]
