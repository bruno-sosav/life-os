from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.negocio.models.proyectos_model import Project
from app.modules.negocio.repositories import proyectos_repository
from app.modules.negocio.schemas.proyectos_schema import ProjectIn, ProjectUpdate


def list_projects(session: Session) -> list[Project]:
    return proyectos_repository.list_projects(session)


def create_project(session: Session, payload: ProjectIn) -> Project:
    return base_repository.save(session, Project(**payload.model_dump()))


def update_project(session: Session, project_id: str, payload: ProjectUpdate) -> Project:
    project = get_or_404(session, Project, project_id)
    return base_repository.save(
        session, base_repository.apply(project, payload.model_dump(exclude_unset=True))
    )


def delete_project(session: Session, project_id: str) -> None:
    """Borra el proyecto con su tablero (ON DELETE CASCADE)."""
    base_repository.delete(session, get_or_404(session, Project, project_id))
