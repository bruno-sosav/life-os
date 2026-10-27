from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.fisico import fisico_service as service
from app.modules.fisico.fisico_model import GymSession, MmaSession, NutritionLog, WeightLog
from app.modules.fisico.fisico_schema import (
    AttendanceDay,
    AttendanceWeek,
    ExerciseProgressionPoint,
    GymSessionCreate,
    GymSessionOut,
    GymSessionUpdate,
    MmaMonth,
    MmaSessionCreate,
    MmaSessionOut,
    MmaSessionUpdate,
    NutritionAverage,
    NutritionLogIn,
    NutritionLogOut,
    WeightLogIn,
    WeightLogOut,
)

router = APIRouter(tags=["fisico"])
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/gym/sessions", response_model=list[GymSessionOut])
def list_gym_sessions(session: SessionDep, limit: int = 50) -> list[GymSession]:
    return service.list_gym_sessions(session, limit)


@router.post("/gym/sessions", response_model=GymSessionOut, status_code=CREATED)
def create_gym_session(payload: GymSessionCreate, session: SessionDep) -> GymSession:
    return service.create_gym_session(session, payload)


@router.patch("/gym/sessions/{session_id}", response_model=GymSessionOut)
def update_gym_session(
    session_id: str, payload: GymSessionUpdate, session: SessionDep
) -> GymSession:
    return service.update_gym_session(session, session_id, payload)


@router.delete("/gym/sessions/{session_id}", status_code=NO_CONTENT)
def delete_gym_session(session_id: str, session: SessionDep) -> Response:
    service.delete_gym_session(session, session_id)
    return Response(status_code=NO_CONTENT)


@router.get("/gym/exercises/names", response_model=list[str])
def list_exercise_names(session: SessionDep) -> list[str]:
    return service.list_exercise_names(session)


@router.get("/gym/exercises/progression", response_model=list[ExerciseProgressionPoint])
def exercise_progression(name: str, session: SessionDep) -> list[ExerciseProgressionPoint]:
    return service.exercise_progression(session, name)


@router.get("/gym/week", response_model=AttendanceWeek)
def gym_week(today: date, session: SessionDep) -> AttendanceWeek:
    return service.attendance_week(session, "gym", today)


@router.put("/gym/attendance/{day}", response_model=AttendanceDay)
def toggle_gym_attendance(day: date, session: SessionDep) -> AttendanceDay:
    return service.toggle_attendance(session, "gym", day)


@router.get("/mma/sessions", response_model=list[MmaSessionOut])
def list_mma_sessions(session: SessionDep) -> list[MmaSession]:
    return service.list_mma_sessions(session)


@router.post("/mma/sessions", response_model=MmaSessionOut, status_code=CREATED)
def create_mma_session(payload: MmaSessionCreate, session: SessionDep) -> MmaSession:
    return service.create_mma_session(session, payload)


@router.patch("/mma/sessions/{session_id}", response_model=MmaSessionOut)
def update_mma_session(
    session_id: str, payload: MmaSessionUpdate, session: SessionDep
) -> MmaSession:
    return service.update_mma_session(session, session_id, payload)


@router.delete("/mma/sessions/{session_id}", status_code=NO_CONTENT)
def delete_mma_session(session_id: str, session: SessionDep) -> Response:
    service.delete_mma_session(session, session_id)
    return Response(status_code=NO_CONTENT)


@router.get("/mma/week", response_model=AttendanceWeek)
def mma_week(today: date, session: SessionDep) -> AttendanceWeek:
    return service.attendance_week(session, "mma", today)


@router.put("/mma/attendance/{day}", response_model=AttendanceDay)
def toggle_mma_attendance(day: date, session: SessionDep) -> AttendanceDay:
    return service.toggle_attendance(session, "mma", day)


@router.get("/mma/month", response_model=MmaMonth)
def mma_month(month: date, session: SessionDep) -> MmaMonth:
    """Calendario del mes que contiene `month`."""
    return service.mma_month(session, month)


@router.get("/weight-logs", response_model=list[WeightLogOut])
def list_weight_logs(session: SessionDep, start: date | None = None) -> list[WeightLog]:
    return service.list_weight_logs(session, start)


@router.put("/weight-logs/{day}", response_model=WeightLogOut)
def upsert_weight_log(day: date, payload: WeightLogIn, session: SessionDep) -> WeightLog:
    return service.upsert_weight_log(session, day, payload)


@router.get("/nutrition-logs", response_model=list[NutritionLogOut])
def list_nutrition_logs(session: SessionDep, start: date | None = None) -> list[NutritionLog]:
    return service.list_nutrition_logs(session, start)


@router.get("/nutrition-logs/average", response_model=NutritionAverage)
def nutrition_average(today: date, session: SessionDep) -> NutritionAverage:
    return service.nutrition_average(session, today)


@router.put("/nutrition-logs/{day}", response_model=NutritionLogOut)
def upsert_nutrition_log(day: date, payload: NutritionLogIn, session: SessionDep) -> NutritionLog:
    return service.upsert_nutrition_log(session, day, payload)
