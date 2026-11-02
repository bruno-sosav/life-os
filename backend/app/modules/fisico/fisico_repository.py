from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Row, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.fisico.fisico_model import (
    Activity,
    ActivitySession,
    NutritionLog,
    SessionExercise,
    WeightLog,
)


# ─── Actividades ────────────────────────────────────────────
def list_activities(session: Session, active: bool | None) -> list[Activity]:
    query = select(Activity).order_by(Activity.sort_order, Activity.created_at)
    if active is not None:
        query = query.where(Activity.active == active)
    return list(session.scalars(query))


# ─── Sesiones ───────────────────────────────────────────────
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


def sessions_between(
    session: Session, activity_id: str, start: date, end: date
) -> list[ActivitySession]:
    query = select(ActivitySession).where(
        ActivitySession.activity_id == activity_id, ActivitySession.date.between(start, end)
    )
    return list(session.scalars(query))


def session_of(session: Session, activity_id: str, day: date) -> ActivitySession | None:
    query = (
        select(ActivitySession)
        .where(ActivitySession.activity_id == activity_id, ActivitySession.date == day)
        .order_by(ActivitySession.created_at.desc())
    )
    return session.scalars(query).first()


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


# ─── Ejercicios ─────────────────────────────────────────────
def list_exercise_names(session: Session, activity_id: str) -> list[str]:
    query = (
        select(SessionExercise.exercise_name)
        .join(ActivitySession)
        .where(ActivitySession.activity_id == activity_id)
        .distinct()
        .order_by(SessionExercise.exercise_name)
    )
    return list(session.scalars(query))


def exercise_progression(
    session: Session, activity_id: str, name: str
) -> Sequence[Row[date, Decimal | None]]:
    """Por fecha: carga máxima del ejercicio. `name` llega en minúsculas (no distingue)."""
    query = (
        select(ActivitySession.date, func.max(SessionExercise.weight_kg))
        .join(ActivitySession)
        .where(ActivitySession.activity_id == activity_id)
        .where(func.lower(SessionExercise.exercise_name) == name)
        .group_by(ActivitySession.date)
        .order_by(ActivitySession.date)
    )
    return session.execute(query).all()


# ─── Peso / Nutrición (un registro por día) ─────────────────
def list_weight_logs(session: Session, start: date | None) -> list[WeightLog]:
    query = select(WeightLog).order_by(WeightLog.date)
    if start is not None:
        query = query.where(WeightLog.date >= start)
    return list(session.scalars(query))


def weight_log_of(session: Session, day: date) -> WeightLog | None:
    return session.scalar(select(WeightLog).where(WeightLog.date == day))


def list_nutrition_logs(session: Session, start: date | None) -> list[NutritionLog]:
    query = select(NutritionLog).order_by(NutritionLog.date)
    if start is not None:
        query = query.where(NutritionLog.date >= start)
    return list(session.scalars(query))


def avg_nutrition_quality(session: Session, start: date, end: date) -> float | None:
    avg = session.scalar(
        select(func.avg(NutritionLog.quality_score)).where(NutritionLog.date.between(start, end))
    )
    return float(avg) if avg is not None else None


def nutrition_log_of(session: Session, day: date) -> NutritionLog | None:
    return session.scalar(select(NutritionLog).where(NutritionLog.date == day))
