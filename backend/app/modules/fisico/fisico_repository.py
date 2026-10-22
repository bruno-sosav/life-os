from collections.abc import Sequence
from datetime import date
from decimal import Decimal

from sqlalchemy import Numeric, Row, func, select, type_coerce
from sqlalchemy.orm import Session, selectinload

from app.modules.fisico.fisico_model import (
    GymExercise,
    GymSession,
    MmaSession,
    NutritionLog,
    WeightLog,
)


# ─── Gym ────────────────────────────────────────────────────
def list_gym_sessions(session: Session, limit: int) -> list[GymSession]:
    query = (
        select(GymSession)
        .options(selectinload(GymSession.exercises))
        .order_by(GymSession.date.desc(), GymSession.created_at.desc())
        .limit(limit)
    )
    return list(session.scalars(query))


def list_exercise_names(session: Session) -> list[str]:
    query = select(GymExercise.exercise_name).distinct().order_by(GymExercise.exercise_name)
    return list(session.scalars(query))


def exercise_progression(
    session: Session, name: str
) -> Sequence[Row[date, Decimal | None, Decimal | None]]:
    """Por fecha: carga máxima y volumen (series × reps × kg) del ejercicio.

    `name` llega en minúsculas: la comparación no distingue mayúsculas.
    """
    volume = type_coerce(
        func.sum(
            func.coalesce(GymExercise.sets, 1)
            * func.coalesce(GymExercise.reps, 0)
            * func.coalesce(GymExercise.weight_kg, 0)
        ),
        Numeric(),
    )
    query = (
        select(GymSession.date, func.max(GymExercise.weight_kg), volume)
        .join(GymSession)
        .where(func.lower(GymExercise.exercise_name) == name)
        .group_by(GymSession.date)
        .order_by(GymSession.date)
    )
    return session.execute(query).all()


# ─── MMA ────────────────────────────────────────────────────
def list_mma_sessions(session: Session) -> list[MmaSession]:
    query = select(MmaSession).order_by(MmaSession.date.desc(), MmaSession.created_at.desc())
    return list(session.scalars(query))


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


def nutrition_log_of(session: Session, day: date) -> NutritionLog | None:
    return session.scalar(select(NutritionLog).where(NutritionLog.date == day))
