from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.negocio.models.proyectos_model import Project


def list_projects(session: Session) -> list[Project]:
    return list(session.scalars(select(Project).order_by(Project.created_at)))


def project_exists(session: Session, project_id: str) -> bool:
    return session.get(Project, project_id) is not None
