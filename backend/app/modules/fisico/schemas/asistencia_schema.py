import datetime as dt

from pydantic import BaseModel

from app.core.base_schema import ORMModel


class LinkedHabitOut(ORMModel):
    id: str
    name: str


class AttendanceDay(BaseModel):
    date: dt.date
    attended: bool


class AttendanceWeek(BaseModel):
    habit: LinkedHabitOut | None  # con hábito vinculado, la asistencia sale de sus registros
    days: list[AttendanceDay]  # lunes a domingo


class MonthDay(BaseModel):
    date: dt.date
    attended: bool | None  # False = sesión sin asistir; None = nada ese día


class ActivityMonth(BaseModel):
    count: int  # días asistidos en el mes
    days: list[MonthDay]
