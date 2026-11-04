from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.negocio.models.proyectos_model import Project
from app.modules.negocio.schemas.proyectos_schema import ProjectIn, ProjectOut, ProjectUpdate
from app.modules.negocio.services import proyectos_service as service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(session: SessionDep) -> list[Project]:
    return service.list_projects(session)


@router.post("/projects", response_model=ProjectOut, status_code=CREATED)
def create_project(payload: ProjectIn, session: SessionDep) -> Project:
    return service.create_project(session, payload)


@router.patch("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: str, payload: ProjectUpdate, session: SessionDep) -> Project:
    return service.update_project(session, project_id, payload)


@router.delete("/projects/{project_id}", status_code=NO_CONTENT)
def delete_project(project_id: str, session: SessionDep) -> Response:
    service.delete_project(session, project_id)
    return Response(status_code=NO_CONTENT)
