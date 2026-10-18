import datetime as dt

from pydantic import BaseModel

from app.schemas.common import ORMModel, UTCDateTime
from app.schemas.rutina import HabitLogOut, HabitOut, RoutineBlockOut


class CompletionRow(ORMModel):
    block_id: str
    date: dt.date


class AttendanceRow(ORMModel):
    date: dt.date
    attended: bool


class WeightRow(ORMModel):
    date: dt.date
    weight_kg: float


class MoodRow(ORMModel):
    date: dt.date
    mood_score: int | None
    sleep_hours: float | None


class DateRow(ORMModel):
    date: dt.date


class BookRow(ORMModel):
    status: str
    finished_at: dt.date | None


class IncomeRow(ORMModel):
    month: dt.date
    amount: float


class ExpenseRow(ORMModel):
    date: dt.date
    amount: float


class CreatedRow(ORMModel):
    created_at: UTCDateTime


class AnalyticsData(BaseModel):
    """Registros crudos que usa la pantalla de Stats (los cálculos los hace el frontend)."""

    habits: list[HabitOut]
    habit_logs: list[HabitLogOut]
    routine_blocks: list[RoutineBlockOut]
    routine_completions: list[CompletionRow]
    gym: list[AttendanceRow]
    mma: list[AttendanceRow]
    weight: list[WeightRow]
    mood: list[MoodRow]
    nutrition: list[DateRow]
    books: list[BookRow]
    finance_income: list[IncomeRow]
    finance_expenses: list[ExpenseRow]
    journal_entries: list[CreatedRow]
