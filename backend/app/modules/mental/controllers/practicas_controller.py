from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.practicas_model import Practice
from app.modules.mental.schemas.practicas_schema import PracticeIn, PracticeOut
from app.modules.mental.services import practicas_service as service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/skills/{skill_id}/practices", response_model=list[PracticeOut])
def list_practices(skill_id: str, session: SessionDep, limit: int = 20) -> list[Practice]:
    return service.list_practices(session, skill_id, limit)


@router.post("/practices", response_model=PracticeOut, status_code=status.HTTP_201_CREATED)
def create_practice(payload: PracticeIn, session: SessionDep) -> Practice:
    return service.create_practice(session, payload)


@router.delete("/practices/{practice_id}", status_code=NO_CONTENT)
def delete_practice(practice_id: str, session: SessionDep) -> Response:
    service.delete_practice(session, practice_id)
    return Response(status_code=NO_CONTENT)
