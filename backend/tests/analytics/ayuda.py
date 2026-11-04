"""Helpers compartidos por los tests de Stats."""

from datetime import date

import pandas as pd

from app.modules.rutina import Habit

TODAY = date(2026, 10, 18)  # domingo

MONDAY = date(2026, 10, 12)


def frame(columns: list[str], rows: list[tuple[object, ...]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=columns)
    for column in ("date", "month"):
        if column in df:
            df[column] = pd.to_datetime(df[column])
    return df


def habit(id_: str, name: str = "Leer", days: list[int] | None = None) -> Habit:
    return Habit(id=id_, name=name, color="#fff", days_of_week=days)


def logs(*items: tuple[str, date]) -> pd.DataFrame:
    return frame(["habit_id", "date"], list(items))
