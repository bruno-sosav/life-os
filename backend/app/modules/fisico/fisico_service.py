import math
from datetime import date, timedelta
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import days_between, month_bounds, week_bounds
from app.modules.fisico import fisico_repository as repository
from app.modules.fisico.fisico_model import (
    Activity,
    ActivitySession,
    NutritionLog,
    SessionExercise,
    WeightLog,
)
from app.modules.fisico.fisico_schema import (
    CHARTABLE,
    ActivityField,
    ActivityIn,
    ActivityMonth,
    ActivityUpdate,
    AttendanceDay,
    AttendanceWeek,
    LinkedHabitOut,
    MonthDay,
    NutritionAverage,
    NutritionLogIn,
    ProgressionPoint,
    SessionIn,
    WeightLogIn,
)
from app.modules.rutina import Habit, HabitLogUpsert, completed_habit_logs, upsert_habit_log

MAX_TEXT = 2000


def _invalid(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail)


# ─── Actividades ────────────────────────────────────────────
def list_activities(session: Session, active: bool | None = None) -> list[Activity]:
    return repository.list_activities(session, active)


def _check_habit(session: Session, habit_id: str | None) -> None:
    if habit_id is not None and session.get(Habit, habit_id) is None:
        raise _invalid("El hábito no existe")


def merge_fields(old: list[dict[str, Any]], new: list[ActivityField]) -> list[dict[str, Any]]:
    """Los campos que ya no vienen quedan archivados: así el historial se sigue leyendo.

    Un campo no puede cambiar de tipo, porque sus valores viejos dejarían de tener sentido.
    """
    previous = {f["id"]: f for f in old}
    for field in new:
        if field.id in previous and previous[field.id]["type"] != field.type:
            raise _invalid(f"'{field.name}' no puede cambiar de tipo: archivalo y creá uno nuevo")
    kept = {f.id for f in new}
    missing = [{**f, "archived": True} for f in old if f["id"] not in kept]
    return [f.model_dump() for f in new] + missing


def create_activity(session: Session, payload: ActivityIn) -> Activity:
    _check_habit(session, payload.habit_id)
    return base_repository.save(session, Activity(**payload.model_dump()))


def update_activity(session: Session, activity_id: str, payload: ActivityUpdate) -> Activity:
    activity = get_or_404(session, Activity, activity_id)
    changes = payload.model_dump(exclude_unset=True)
    if "habit_id" in changes:
        _check_habit(session, changes["habit_id"])
    if payload.fields is None:
        changes.pop("fields", None)
    else:
        changes["fields"] = merge_fields(activity.fields, payload.fields)
    return base_repository.save(session, base_repository.apply(activity, changes))


def delete_activity(session: Session, activity_id: str) -> None:
    """Borra la actividad con todas sus sesiones. Para dejar de verla sin perder nada: pausarla."""
    base_repository.delete(session, get_or_404(session, Activity, activity_id))


# ─── Sesiones ───────────────────────────────────────────────
def _check_value(field: dict[str, Any], value: Any) -> Any:
    kind = field["type"]
    is_number = isinstance(value, int | float) and not isinstance(value, bool)
    valid = {
        "numero": is_number and math.isfinite(value),
        "texto": isinstance(value, str) and len(value) <= MAX_TEXT,
        "si_no": isinstance(value, bool),
        "opcion": value in (field["options"] or []),
        "escala": is_number and value in (1, 2, 3, 4, 5),
    }.get(kind, False)
    if not valid:
        raise _invalid(f"Valor inválido para '{field['name']}'")
    if kind == "numero":
        return float(value)
    return int(value) if kind == "escala" else value


def clean_values(fields: list[dict[str, Any]], values: dict[str, Any]) -> dict[str, Any]:
    """Valida cada valor contra su campo. Un valor vacío (None o "") no se guarda."""
    by_id = {f["id"]: f for f in fields if not f["archived"] and f["type"] != "ejercicios"}
    clean = {}
    for field_id, value in values.items():
        if field_id not in by_id:
            raise _invalid(f"La actividad no tiene el campo {field_id}")
        if value is not None and value != "":
            clean[field_id] = _check_value(by_id[field_id], value)
    return clean


def _has_exercises(activity: Activity) -> bool:
    return any(f["type"] == "ejercicios" and not f["archived"] for f in activity.fields)


def list_sessions(session: Session, activity_id: str | None, limit: int) -> list[ActivitySession]:
    return repository.list_sessions(session, activity_id, limit)


def create_session(session: Session, payload: SessionIn) -> ActivitySession:
    """Crea la sesión y sus ejercicios en una sola transacción."""
    activity = session.get(Activity, payload.activity_id)
    if activity is None:
        raise _invalid("La actividad no existe")
    if payload.exercises and not _has_exercises(activity):
        raise _invalid(f"'{activity.name}' no tiene lista de ejercicios")
    record = ActivitySession(
        **payload.model_dump(exclude={"values", "exercises"}),
        values=clean_values(activity.fields, payload.values),
    )
    record.exercises = [SessionExercise(**e.model_dump()) for e in payload.exercises]
    return base_repository.save(session, record)


def delete_session(session: Session, session_id: str) -> None:
    base_repository.delete(session, get_or_404(session, ActivitySession, session_id))


def attended_days(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(activity_id, día) en que se hizo cada actividad, una vez por día.

    Cuenta la sesión asistida o, si la actividad tiene hábito vinculado, el hábito cumplido:
    marcar la asistencia en el hábito no crea sesión, pero igual es un día entrenado.
    """
    days = set(repository.attended_sessions(session, start, end))
    linked: dict[str, list[str]] = {}
    for activity in repository.list_activities(session, None):
        if activity.habit_id:
            linked.setdefault(activity.habit_id, []).append(activity.id)
    for habit_id, day in completed_habit_logs(session, start, end):
        days.update((activity_id, day) for activity_id in linked.get(habit_id, []))
    return sorted(days)


# ─── Asistencia y calendario ────────────────────────────────
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
        sessions = repository.sessions_between(session, activity.id, days[0], days[-1])
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

    record = repository.session_of(session, activity.id, day)
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
    missed = {
        s.date for s in repository.sessions_between(session, activity.id, days[0], days[-1])
    } - attended
    return ActivityMonth(
        count=len(attended),
        days=[
            MonthDay(date=d, attended=True if d in attended else False if d in missed else None)
            for d in days
        ],
    )


def list_exercise_names(session: Session, activity_id: str) -> list[str]:
    return repository.list_exercise_names(session, activity_id)


def exercise_progression(session: Session, activity_id: str, name: str) -> list[ProgressionPoint]:
    rows = repository.exercise_progression(session, activity_id, name.strip().lower())
    return [
        ProgressionPoint(date=day, value=float(kg) if kg is not None else None) for day, kg in rows
    ]


def field_series(session: Session, activity_id: str, field_id: str) -> list[ProgressionPoint]:
    """Un punto por sesión con valor en ese campo (número o escala), en orden de fecha."""
    activity = get_or_404(session, Activity, activity_id)
    field = next((f for f in activity.fields if f["id"] == field_id), None)
    if field is None or field["type"] not in CHARTABLE:
        raise _invalid("Ese campo no se puede graficar")
    return [
        ProgressionPoint(date=day, value=float(values[field_id]))
        for day, values in repository.field_values(session, activity.id)
        if isinstance(values.get(field_id), int | float)
    ]


# ─── Peso ───────────────────────────────────────────────────
def list_weight_logs(session: Session, start: date | None) -> list[WeightLog]:
    return repository.list_weight_logs(session, start)


def upsert_weight_log(session: Session, day: date, payload: WeightLogIn) -> WeightLog:
    log = repository.weight_log_of(session, day) or WeightLog(date=day)
    return base_repository.save(session, base_repository.apply(log, payload.model_dump()))


# ─── Nutrición ──────────────────────────────────────────────
def list_nutrition_logs(session: Session, start: date | None) -> list[NutritionLog]:
    return repository.list_nutrition_logs(session, start)


def nutrition_average(session: Session, today: date) -> NutritionAverage:
    avg = repository.avg_nutrition_quality(session, today - timedelta(days=6), today)
    return NutritionAverage(avg_quality=round(avg, 1) if avg is not None else None)


def upsert_nutrition_log(session: Session, day: date, payload: NutritionLogIn) -> NutritionLog:
    log = repository.nutrition_log_of(session, day) or NutritionLog(date=day)
    return base_repository.save(session, base_repository.apply(log, payload.model_dump()))
