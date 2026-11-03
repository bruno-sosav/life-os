from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.fisico.models.sesiones_model import ActivitySession
from app.modules.fisico.schemas.sesiones_schema import ProgressionPoint, SessionIn, SessionOut
from app.modules.fisico.services import sesiones_service as service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


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
