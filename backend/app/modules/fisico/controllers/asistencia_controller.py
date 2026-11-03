from datetime import date

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.fisico.schemas.asistencia_schema import (
    ActivityMonth,
    AttendanceDay,
    AttendanceWeek,
)
from app.modules.fisico.services import asistencia_service as service

router = APIRouter()


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
