import calendar
from datetime import date, timedelta

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
    AttendanceDay,
    AttendanceWeek,
    ExerciseProgressionPoint,
    GymSessionCreate,
    GymSessionUpdate,
    LinkedHabitOut,
    MmaMonth,
    MmaMonthDay,
    MmaSessionCreate,
    MmaSessionUpdate,
    NutritionAverage,
    NutritionLogIn,
    WeightLogIn,
)
from app.modules.rutina import HabitLogUpsert, LinkedModule, upsert_habit_log

SESSION_MODELS: dict[LinkedModule, type[GymSession | MmaSession]] = {
    "gym": GymSession,
    "mma": MmaSession,
}


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


def mma_month(session: Session, month: date) -> MmaMonth:
    """Calendario del mes de `month`: un día por fecha, con o sin sesión."""
    first = month.replace(day=1)
    length = calendar.monthrange(first.year, first.month)[1]
    days = [first + timedelta(days=i) for i in range(length)]
    sessions = repository.list_mma_sessions_between(session, days[0], days[-1])
    by_date = {s.date: s.attended for s in sessions}
    return MmaMonth(
        count=len(sessions),
        days=[MmaMonthDay(date=d, attended=by_date.get(d)) for d in days],
    )


# ─── Asistencia (gym y MMA) ─────────────────────────────────
def attendance_week(session: Session, module: LinkedModule, today: date) -> AttendanceWeek:
    """Asistencia de lunes a domingo: del hábito vinculado si hay uno, si no de las sesiones."""
    monday = today - timedelta(days=today.weekday())
    days = [monday + timedelta(days=i) for i in range(7)]
    habit = repository.linked_habit(session, module)
    if habit:
        done = repository.completed_habit_dates(session, habit.id, days[0], days[-1])
    else:
        done = repository.attended_dates(session, SESSION_MODELS[module], days[0], days[-1])
    return AttendanceWeek(
        habit=LinkedHabitOut.model_validate(habit) if habit else None,
        days=[AttendanceDay(date=d, attended=d in done) for d in days],
    )


def toggle_attendance(session: Session, module: LinkedModule, day: date) -> AttendanceDay:
    """Alterna la asistencia de `day` en el hábito vinculado o, si no hay, en la sesión del día."""
    habit = repository.linked_habit(session, module)
    if habit:
        done = day in repository.completed_habit_dates(session, habit.id, day, day)
        upsert_habit_log(session, HabitLogUpsert(habit_id=habit.id, date=day, completed=not done))
        return AttendanceDay(date=day, attended=not done)

    existing: GymSession | MmaSession | None = (
        repository.session_of(session, GymSession, day)
        if module == "gym"
        else repository.session_of(session, MmaSession, day)
    )
    if existing:
        existing.attended = not existing.attended
        base_repository.save(session, existing)
        return AttendanceDay(date=day, attended=existing.attended)
    new = GymSession(date=day) if module == "gym" else MmaSession(date=day, session_type="técnica")
    new.attended = True
    base_repository.save(session, new)
    return AttendanceDay(date=day, attended=True)


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


def nutrition_average(session: Session, today: date) -> NutritionAverage:
    avg = repository.avg_nutrition_quality(session, today - timedelta(days=6), today)
    return NutritionAverage(avg_quality=round(avg, 1) if avg is not None else None)


def upsert_nutrition_log(session: Session, day: date, payload: NutritionLogIn) -> NutritionLog:
    log = repository.nutrition_log_of(session, day) or NutritionLog(date=day)
    for field, value in payload.model_dump().items():
        setattr(log, field, value)
    return base_repository.save(session, log)
