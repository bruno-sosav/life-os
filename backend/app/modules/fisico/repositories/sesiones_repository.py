from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.fisico.models.sesiones_model import ActivitySession, SessionExercise


def list_sessions(session: Session, activity_id: str | None, limit: int) -> list[ActivitySession]:
    query = (
        select(ActivitySession)
        .options(selectinload(ActivitySession.exercises))
        .order_by(ActivitySession.date.desc(), ActivitySession.created_at.desc())
        .limit(limit)
    )
    if activity_id is not None:
        query = query.where(ActivitySession.activity_id == activity_id)
    return list(session.scalars(query))


def attended_on(session: Session, activity_id: str, day: date) -> int:
    """Cuántas sesiones asistidas tiene la actividad ese día."""
    query = select(func.count()).where(
        ActivitySession.activity_id == activity_id,
        ActivitySession.date == day,
        ActivitySession.attended.is_(True),
    )
    return int(session.scalar(query) or 0)


def attended_sessions(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(activity_id, fecha) de cada sesión asistida en el rango, de cualquier actividad."""
    query = select(ActivitySession.activity_id, ActivitySession.date).where(
        ActivitySession.attended.is_(True), ActivitySession.date.between(start, end)
    )
    return [(activity_id, day) for activity_id, day in session.execute(query)]


def field_values(session: Session, activity_id: str) -> list[tuple[date, dict[str, Any]]]:
    query = (
        select(ActivitySession.date, ActivitySession.values)
        .where(ActivitySession.activity_id == activity_id)
        .order_by(ActivitySession.date, ActivitySession.created_at)
    )
    return [(day, values) for day, values in session.execute(query)]


def list_exercise_names(session: Session) -> list[str]:
    """Los ejercicios que ya usaste, en cualquier tipo, del más hecho al menos.

    Sin distinguir mayúsculas: "Sentadilla" y "sentadilla" son el mismo.
    """
    key = func.lower(SessionExercise.exercise_name)
    query = (
        select(func.max(SessionExercise.exercise_name))
        .group_by(key)
        .order_by(func.count().desc(), key)
    )
    return [name for name in session.scalars(query) if name]


def last_exercise(session: Session, name: str) -> list[tuple[ActivitySession, SessionExercise]]:
    """Las filas de ese ejercicio en la última sesión que lo tuvo. `name` llega en minúsculas."""
    query = (
        select(ActivitySession, SessionExercise)
        .join(ActivitySession, ActivitySession.id == SessionExercise.session_id)
        .where(func.lower(SessionExercise.exercise_name) == name)
        .order_by(ActivitySession.date.desc(), ActivitySession.created_at.desc())
    )
    rows = [(s, e) for s, e in session.execute(query)]
    return [(s, e) for s, e in rows if s.id == rows[0][0].id] if rows else []


def exercise_progression(session: Session, name: str) -> Sequence[Row[date, Decimal | None]]:
    """Por fecha: carga máxima del ejercicio, en cualquier tipo. `name` llega en minúsculas."""
    query = (
        select(ActivitySession.date, func.max(SessionExercise.weight_kg))
        .join(ActivitySession)
        .where(func.lower(SessionExercise.exercise_name) == name)
        .group_by(ActivitySession.date)
        .order_by(ActivitySession.date)
    )
    return session.execute(query).all()
