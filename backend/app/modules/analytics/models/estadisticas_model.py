"""Lo que necesitan los cálculos de Stats, ya leído de la base.

Los cálculos son funciones puras: reciben esto (DataFrames con una columna `date` de tipo
datetime64) y devuelven estructuras listas para serializar.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Any

import pandas as pd

from app.modules.fisico import Activity
from app.modules.mental import Skill
from app.modules.rutina import Habit, RoutineBlock


def _empty(*columns: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            c: pd.Series(dtype="datetime64[ns]" if c in ("date", "month") else "object")
            for c in columns
        }
    )


@dataclass
class StatsInput:
    today: date
    habits: Sequence[Habit] = ()
    blocks: Sequence[RoutineBlock] = ()
    # Hábitos completados (solo hábitos activos): habit_id, date
    habit_logs: pd.DataFrame = field(default_factory=lambda: _empty("habit_id", "date"))
    # Bloques completados: block_id, date
    completions: pd.DataFrame = field(default_factory=lambda: _empty("block_id", "date"))
    # Todas las actividades (también las pausadas: sus sesiones viejas siguen contando)
    activities: Sequence[Activity] = ()
    # Días con cada actividad (sesión asistida o hábito vinculado cumplido): activity_id, date
    workouts: pd.DataFrame = field(default_factory=lambda: _empty("activity_id", "date"))
    weights: pd.DataFrame = field(default_factory=lambda: _empty("date", "kg"))
    # Skills de Mental (con su meta semanal) y sus prácticas: skill_id, date, minutes
    skills: Sequence[Skill] = ()
    practices: pd.DataFrame = field(default_factory=lambda: _empty("skill_id", "date", "minutes"))
    books_finished: Sequence[date] = ()
    income: pd.DataFrame = field(default_factory=lambda: _empty("month", "amount"))
    expenses: pd.DataFrame = field(default_factory=lambda: _empty("date", "amount"))


def ts(day: date) -> pd.Timestamp:
    return pd.Timestamp(day)


def between(df: pd.DataFrame, start: date, end: date, column: str = "date") -> pd.DataFrame:
    return df[(df[column] >= ts(start)) & (df[column] <= ts(end))]


def day_range(start: date, end: date) -> pd.DatetimeIndex:
    return pd.date_range(ts(start), ts(end), freq="D")


def frame(rows: list[tuple[Any, ...]], columns: list[str], dates: tuple[str, ...]) -> pd.DataFrame:
    """Filas leídas de la base → DataFrame, con las columnas de fecha como datetime64."""
    df = pd.DataFrame(rows, columns=columns)
    for column in dates:
        df[column] = pd.to_datetime(df[column])
    return df
