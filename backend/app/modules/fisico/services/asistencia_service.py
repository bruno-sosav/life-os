from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import days_between, month_bounds, week_bounds
from app.modules.fisico.models.actividades_model import Activity
from app.modules.fisico.models.sesiones_model import ActivitySession
from app.modules.fisico.repositories import actividades_repository, sesiones_repository
from app.modules.fisico.schemas.asistencia_schema import (
    ActivityMonth,
    AttendanceDay,
    AttendanceWeek,
    LinkedHabitOut,
    MonthDay,
)
from app.modules.rutina import Habit, HabitLogUpsert, completed_habit_logs, upsert_habit_log


def attended_days(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(activity_id, día) en que se hizo cada actividad, una vez por día.

    Cuenta la sesión asistida o, si la actividad tiene hábito vinculado, el hábito cumplido:
    marcar la asistencia en el hábito no crea sesión, pero igual es un día entrenado.
    """
    days = set(sesiones_repository.attended_sessions(session, start, end))
    linked: dict[str, list[str]] = {}
    for activity in actividades_repository.list_activities(session, None):
        if activity.habit_id:
            linked.setdefault(activity.habit_id, []).append(activity.id)
    for habit_id, day in completed_habit_logs(session, start, end):
        days.update((activity_id, day) for activity_id in linked.get(habit_id, []))
    return sorted(days)


def _linked_habit(session: Session, activity: Activity) -> Habit | None:
    habit = session.get(Habit, activity.habit_id) if activity.habit_id else None
    return habit if habit is not None and habit.active else None


def _habit_done_dates(session: Session, habit_id: str, start: date, end: date) -> set[date]:
    return {day for hid, day in completed_habit_logs(session, start, end) if hid == habit_id}


def attendance_week(session: Session, activity_id: str, today: date) -> AttendanceWeek:
    """Asistencia de lunes a domingo: del hábito vinculado si hay uno, si no de las sesiones."""
    activity = get_or_404(session, Activity, activity_id)
    days = days_between(week_bounds(today))
    habit = _linked_habit(session, activity)
    if habit:
        done = _habit_done_dates(session, habit.id, days[0], days[-1])
    else:
        sessions = sesiones_repository.sessions_between(session, activity.id, days[0], days[-1])
        done = {s.date for s in sessions if s.attended}
    return AttendanceWeek(
        habit=LinkedHabitOut.model_validate(habit) if habit else None,
        days=[AttendanceDay(date=d, attended=d in done) for d in days],
    )


def toggle_attendance(session: Session, activity_id: str, day: date) -> AttendanceDay:
    """Alterna la asistencia de `day` en el hábito vinculado o, si no hay, en la sesión del día."""
    activity = get_or_404(session, Activity, activity_id)
    habit = _linked_habit(session, activity)
    if habit:
        done = day in _habit_done_dates(session, habit.id, day, day)
        upsert_habit_log(session, HabitLogUpsert(habit_id=habit.id, date=day, completed=not done))
        return AttendanceDay(date=day, attended=not done)

    record = sesiones_repository.session_of(session, activity.id, day)
    if record is None:
        record = ActivitySession(activity_id=activity.id, date=day, attended=True, values={})
    else:
        record.attended = not record.attended
    base_repository.save(session, record)
    return AttendanceDay(date=day, attended=record.attended)


def activity_month(session: Session, activity_id: str, month: date) -> ActivityMonth:
    """Calendario del mes: asistió (sesión o hábito vinculado), faltó (sesión sin asistir) o nada.

    Usa la misma regla que la semana y el dashboard (`attended_days`).
    """
    activity = get_or_404(session, Activity, activity_id)
    days = days_between(month_bounds(month))
    attended = {d for aid, d in attended_days(session, days[0], days[-1]) if aid == activity.id}
    sessions = sesiones_repository.sessions_between(session, activity.id, days[0], days[-1])
    missed = {s.date for s in sessions} - attended
    return ActivityMonth(
        count=len(attended),
        days=[
            MonthDay(date=d, attended=True if d in attended else False if d in missed else None)
            for d in days
        ],
    )
