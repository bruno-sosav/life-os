from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.fisico import fisico_service as service
from app.modules.fisico.fisico_model import Activity, ActivitySession, NutritionLog, WeightLog
from app.modules.fisico.fisico_schema import (
    ActivityIn,
    ActivityMonth,
    ActivityOut,
    ActivityUpdate,
    AttendanceDay,
    AttendanceWeek,
    NutritionAverage,
    NutritionLogIn,
    NutritionLogOut,
    ProgressionPoint,
    SessionIn,
    SessionOut,
    WeightLogIn,
    WeightLogOut,
)

router = APIRouter(tags=["fisico"])
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/activities", response_model=list[ActivityOut])
def list_activities(session: SessionDep, active: bool | None = None) -> list[Activity]:
    return service.list_activities(session, active)


@router.post("/activities", response_model=ActivityOut, status_code=CREATED)
def create_activity(payload: ActivityIn, session: SessionDep) -> Activity:
    return service.create_activity(session, payload)


@router.patch("/activities/{activity_id}", response_model=ActivityOut)
def update_activity(activity_id: str, payload: ActivityUpdate, session: SessionDep) -> Activity:
    return service.update_activity(session, activity_id, payload)


@router.delete("/activities/{activity_id}", status_code=NO_CONTENT)
def delete_activity(activity_id: str, session: SessionDep) -> Response:
    service.delete_activity(session, activity_id)
    return Response(status_code=NO_CONTENT)


@router.get("/activities/{activity_id}/week", response_model=AttendanceWeek)
def attendance_week(activity_id: str, today: date, session: SessionDep) -> AttendanceWeek:
    return service.attendance_week(session, activity_id, today)


@router.put("/activities/{activity_id}/attendance/{day}", response_model=AttendanceDay)
def toggle_attendance(activity_id: str, day: date, session: SessionDep) -> AttendanceDay:
    return service.toggle_attendance(session, activity_id, day)


@router.get("/activities/{activity_id}/month", response_model=ActivityMonth)
def activity_month(activity_id: str, month: date, session: SessionDep) -> ActivityMonth:
    """Calendario del mes que contiene `month`."""
    return service.activity_month(session, activity_id, month)


@router.get("/activities/{activity_id}/exercises/names", response_model=list[str])
def list_exercise_names(activity_id: str, session: SessionDep) -> list[str]:
    return service.list_exercise_names(session, activity_id)


@router.get(
    "/activities/{activity_id}/exercises/progression", response_model=list[ProgressionPoint]
)
def exercise_progression(
    activity_id: str, name: str, session: SessionDep
) -> list[ProgressionPoint]:
    return service.exercise_progression(session, activity_id, name)


@router.get(
    "/activities/{activity_id}/fields/{field_id}/series", response_model=list[ProgressionPoint]
)
def field_series(activity_id: str, field_id: str, session: SessionDep) -> list[ProgressionPoint]:
    return service.field_series(session, activity_id, field_id)


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    session: SessionDep, activity_id: str | None = None, limit: int = 50
) -> list[ActivitySession]:
    return service.list_sessions(session, activity_id, limit)


@router.post("/sessions", response_model=SessionOut, status_code=CREATED)
def create_session(payload: SessionIn, session: SessionDep) -> ActivitySession:
    return service.create_session(session, payload)


@router.delete("/sessions/{session_id}", status_code=NO_CONTENT)
def delete_session(session_id: str, session: SessionDep) -> Response:
    service.delete_session(session, session_id)
    return Response(status_code=NO_CONTENT)


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
