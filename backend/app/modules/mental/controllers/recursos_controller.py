from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.recursos_model import SkillResource
from app.modules.mental.schemas.recursos_schema import ResourceIn, ResourceOut
from app.modules.mental.services import recursos_service as service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.post(
    "/skills/{skill_id}/resources", response_model=ResourceOut, status_code=status.HTTP_201_CREATED
)
def create_resource(skill_id: str, payload: ResourceIn, session: SessionDep) -> SkillResource:
    return service.create_resource(session, skill_id, payload)


@router.delete("/skill-resources/{resource_id}", status_code=NO_CONTENT)
def delete_resource(resource_id: str, session: SessionDep) -> Response:
    service.delete_resource(session, resource_id)
    return Response(status_code=NO_CONTENT)
