from datetime import date

from sqlalchemy.orm import Session

from app.core.fechas_util import Period, days_between, month_bounds, week_bounds
from app.modules.fisico.repositories import actividades_repository, sesiones_repository
from app.modules.fisico.schemas.asistencia_schema import TrainingDay, TrainingDays
from app.modules.rutina import completed_habit_logs


def attended_days(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(activity_id, día) en que se hizo cada actividad, una vez por día.

    Cuenta la sesión asistida o, si la actividad tiene hábito vinculado, el hábito cumplido
    (marcado desde el dashboard): igual es un día entrenado.
    """
    days = set(sesiones_repository.attended_sessions(session, start, end))
    linked: dict[str, list[str]] = {}
    for activity in actividades_repository.list_activities(session, None):
        if activity.habit_id:
            linked.setdefault(activity.habit_id, []).append(activity.id)
    for habit_id, day in completed_habit_logs(session, start, end):
        days.update((activity_id, day) for activity_id in linked.get(habit_id, []))
    return sorted(days)


def _training(session: Session, period: Period) -> TrainingDays:
    by_day: dict[date, list[str]] = {}
    for activity_id, day in attended_days(session, period.start, period.end):
        by_day.setdefault(day, []).append(activity_id)
    return TrainingDays(
        count=len(by_day),
        days=[TrainingDay(date=d, activity_ids=by_day.get(d, [])) for d in days_between(period)],
    )


def training_week(session: Session, today: date) -> TrainingDays:
    """Lunes a domingo de la semana de `today`, con lo que entrenaste cada día."""
    return _training(session, week_bounds(today))


def training_month(session: Session, month: date) -> TrainingDays:
    """Todos los días del mes que contiene `month`, con lo que entrenaste cada día."""
    return _training(session, month_bounds(month))
