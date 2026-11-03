from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.fisico.models.actividades_model import Activity
from app.modules.fisico.schemas.actividades_schema import ActivityIn, ActivityOut, ActivityUpdate
from app.modules.fisico.services import actividades_service as service

router = APIRouter()
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
