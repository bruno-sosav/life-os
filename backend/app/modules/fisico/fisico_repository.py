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
from app.modules.rutina import Habit, HabitLog


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


def list_mma_sessions_between(session: Session, start: date, end: date) -> list[MmaSession]:
    return list(session.scalars(select(MmaSession).where(MmaSession.date.between(start, end))))


# ─── Asistencia (gym y MMA) ─────────────────────────────────
def linked_habit(session: Session, module: str) -> Habit | None:
    query = select(Habit).where(Habit.active.is_(True), Habit.linked_module == module)
    return session.scalars(query.order_by(Habit.sort_order, Habit.created_at)).first()


def completed_habit_dates(session: Session, habit_id: str, start: date, end: date) -> set[date]:
    query = select(HabitLog.date).where(
        HabitLog.habit_id == habit_id,
        HabitLog.completed.is_(True),
        HabitLog.date.between(start, end),
    )
    return set(session.scalars(query))


def attended_dates(
    session: Session, model: type[GymSession | MmaSession], start: date, end: date
) -> set[date]:
    query = select(model.date).where(model.attended.is_(True), model.date.between(start, end))
    return set(session.scalars(query))


def session_of[T: (GymSession, MmaSession)](
    session: Session, model: type[T], day: date
) -> T | None:
    query = select(model).where(model.date == day).order_by(model.created_at.desc())
    return session.scalars(query).first()


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
