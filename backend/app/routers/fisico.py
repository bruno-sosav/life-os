from datetime import date

from fastapi import APIRouter, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db import SessionDep
from app.models import GymExercise, GymSession, MmaSession, NutritionLog, WeightLog
from app.routers.common import get_or_404
from app.schemas.fisico import (
    ExerciseProgressionPoint,
    GymSessionCreate,
    GymSessionOut,
    GymSessionUpdate,
    MmaSessionCreate,
    MmaSessionOut,
    MmaSessionUpdate,
    NutritionLogIn,
    NutritionLogOut,
    WeightLogIn,
    WeightLogOut,
)

router = APIRouter(tags=["fisico"])


# ─── Gym ────────────────────────────────────────────────────
@router.get("/gym/sessions", response_model=list[GymSessionOut])
def list_gym_sessions(session: SessionDep, limit: int = 50) -> list[GymSession]:
    query = (
        select(GymSession)
        .options(selectinload(GymSession.exercises))
        .order_by(GymSession.date.desc(), GymSession.created_at.desc())
        .limit(limit)
    )
    return list(session.scalars(query))


@router.post("/gym/sessions", response_model=GymSessionOut, status_code=status.HTTP_201_CREATED)
def create_gym_session(payload: GymSessionCreate, session: SessionDep) -> GymSession:
    """Crea la sesión y sus ejercicios en una sola transacción."""
    gym_session = GymSession(**payload.model_dump(exclude={"exercises"}))
    gym_session.exercises = [GymExercise(**e.model_dump()) for e in payload.exercises]
    session.add(gym_session)
    session.commit()
    session.refresh(gym_session)
    return gym_session


@router.patch("/gym/sessions/{session_id}", response_model=GymSessionOut)
def update_gym_session(
    session_id: str, payload: GymSessionUpdate, session: SessionDep
) -> GymSession:
    gym_session = get_or_404(session, GymSession, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(gym_session, field, value)
    session.commit()
    return gym_session


@router.delete("/gym/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_gym_session(session_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, GymSession, session_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/gym/exercises/names", response_model=list[str])
def list_exercise_names(session: SessionDep) -> list[str]:
    query = select(GymExercise.exercise_name).distinct().order_by(GymExercise.exercise_name)
    return list(session.scalars(query))


@router.get("/gym/exercises/progression", response_model=list[ExerciseProgressionPoint])
def exercise_progression(name: str, session: SessionDep) -> list[ExerciseProgressionPoint]:
    """Carga máxima y volumen por sesión para un ejercicio (sin distinguir mayúsculas)."""
    volume = func.sum(
        func.coalesce(GymExercise.sets, 1)
        * func.coalesce(GymExercise.reps, 0)
        * func.coalesce(GymExercise.weight_kg, 0)
    )
    query = (
        select(GymSession.date, func.max(GymExercise.weight_kg), volume)
        .join(GymSession)
        .where(func.lower(GymExercise.exercise_name) == name.strip().lower())
        .group_by(GymSession.date)
        .order_by(GymSession.date)
    )
    return [
        ExerciseProgressionPoint(
            date=day,
            max_weight_kg=float(max_weight) if max_weight is not None else None,
            volume_kg=float(vol) if vol is not None else None,
        )
        for day, max_weight, vol in session.execute(query)
    ]


# ─── MMA ────────────────────────────────────────────────────
@router.get("/mma/sessions", response_model=list[MmaSessionOut])
def list_mma_sessions(session: SessionDep) -> list[MmaSession]:
    query = select(MmaSession).order_by(MmaSession.date.desc(), MmaSession.created_at.desc())
    return list(session.scalars(query))


@router.post("/mma/sessions", response_model=MmaSessionOut, status_code=status.HTTP_201_CREATED)
def create_mma_session(payload: MmaSessionCreate, session: SessionDep) -> MmaSession:
    mma_session = MmaSession(**payload.model_dump())
    session.add(mma_session)
    session.commit()
    session.refresh(mma_session)
    return mma_session


@router.patch("/mma/sessions/{session_id}", response_model=MmaSessionOut)
def update_mma_session(
    session_id: str, payload: MmaSessionUpdate, session: SessionDep
) -> MmaSession:
    mma_session = get_or_404(session, MmaSession, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(mma_session, field, value)
    session.commit()
    return mma_session


@router.delete("/mma/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mma_session(session_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, MmaSession, session_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Peso ───────────────────────────────────────────────────
@router.get("/weight-logs", response_model=list[WeightLogOut])
def list_weight_logs(session: SessionDep, start: date | None = None) -> list[WeightLog]:
    query = select(WeightLog).order_by(WeightLog.date)
    if start is not None:
        query = query.where(WeightLog.date >= start)
    return list(session.scalars(query))


@router.put("/weight-logs/{day}", response_model=WeightLogOut)
def upsert_weight_log(day: date, payload: WeightLogIn, session: SessionDep) -> WeightLog:
    log = session.scalar(select(WeightLog).where(WeightLog.date == day))
    if log is None:
        log = WeightLog(date=day, weight_kg=payload.weight_kg)
        session.add(log)
    for field, value in payload.model_dump().items():
        setattr(log, field, value)
    session.commit()
    session.refresh(log)
    return log


# ─── Nutrición ──────────────────────────────────────────────
@router.get("/nutrition-logs", response_model=list[NutritionLogOut])
def list_nutrition_logs(session: SessionDep, start: date | None = None) -> list[NutritionLog]:
    query = select(NutritionLog).order_by(NutritionLog.date)
    if start is not None:
        query = query.where(NutritionLog.date >= start)
    return list(session.scalars(query))


@router.put("/nutrition-logs/{day}", response_model=NutritionLogOut)
def upsert_nutrition_log(day: date, payload: NutritionLogIn, session: SessionDep) -> NutritionLog:
    log = session.scalar(select(NutritionLog).where(NutritionLog.date == day))
    if log is None:
        log = NutritionLog(date=day)
        session.add(log)
    for field, value in payload.model_dump().items():
        setattr(log, field, value)
    session.commit()
    session.refresh(log)
    return log
