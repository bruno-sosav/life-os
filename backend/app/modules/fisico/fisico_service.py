from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.fisico import fisico_repository as repository
from app.modules.fisico.fisico_model import (
    GymExercise,
    GymSession,
    MmaSession,
    NutritionLog,
    WeightLog,
)
from app.modules.fisico.fisico_schema import (
    ExerciseProgressionPoint,
    GymSessionCreate,
    GymSessionUpdate,
    MmaSessionCreate,
    MmaSessionUpdate,
    NutritionLogIn,
    WeightLogIn,
)


# ─── Gym ────────────────────────────────────────────────────
def list_gym_sessions(session: Session, limit: int) -> list[GymSession]:
    return repository.list_gym_sessions(session, limit)


def create_gym_session(session: Session, payload: GymSessionCreate) -> GymSession:
    """Crea la sesión y sus ejercicios en una sola transacción."""
    gym_session = GymSession(**payload.model_dump(exclude={"exercises"}))
    gym_session.exercises = [GymExercise(**e.model_dump()) for e in payload.exercises]
    return base_repository.save(session, gym_session)


def update_gym_session(session: Session, session_id: str, payload: GymSessionUpdate) -> GymSession:
    gym_session = get_or_404(session, GymSession, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(gym_session, field, value)
    return base_repository.save(session, gym_session)


def delete_gym_session(session: Session, session_id: str) -> None:
    base_repository.delete(session, get_or_404(session, GymSession, session_id))


def list_exercise_names(session: Session) -> list[str]:
    return repository.list_exercise_names(session)


def exercise_progression(session: Session, name: str) -> list[ExerciseProgressionPoint]:
    return [
        ExerciseProgressionPoint(
            date=day,
            max_weight_kg=float(max_weight) if max_weight is not None else None,
            volume_kg=float(volume) if volume is not None else None,
        )
        for day, max_weight, volume in repository.exercise_progression(
            session, name.strip().lower()
        )
    ]


# ─── MMA ────────────────────────────────────────────────────
def list_mma_sessions(session: Session) -> list[MmaSession]:
    return repository.list_mma_sessions(session)


def create_mma_session(session: Session, payload: MmaSessionCreate) -> MmaSession:
    return base_repository.save(session, MmaSession(**payload.model_dump()))


def update_mma_session(session: Session, session_id: str, payload: MmaSessionUpdate) -> MmaSession:
    mma_session = get_or_404(session, MmaSession, session_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(mma_session, field, value)
    return base_repository.save(session, mma_session)


def delete_mma_session(session: Session, session_id: str) -> None:
    base_repository.delete(session, get_or_404(session, MmaSession, session_id))


# ─── Peso ───────────────────────────────────────────────────
def list_weight_logs(session: Session, start: date | None) -> list[WeightLog]:
    return repository.list_weight_logs(session, start)


def upsert_weight_log(session: Session, day: date, payload: WeightLogIn) -> WeightLog:
    log = repository.weight_log_of(session, day) or WeightLog(date=day)
    for field, value in payload.model_dump().items():
        setattr(log, field, value)
    return base_repository.save(session, log)


# ─── Nutrición ──────────────────────────────────────────────
def list_nutrition_logs(session: Session, start: date | None) -> list[NutritionLog]:
    return repository.list_nutrition_logs(session, start)


def upsert_nutrition_log(session: Session, day: date, payload: NutritionLogIn) -> NutritionLog:
    log = repository.nutrition_log_of(session, day) or NutritionLog(date=day)
    for field, value in payload.model_dump().items():
        setattr(log, field, value)
    return base_repository.save(session, log)
