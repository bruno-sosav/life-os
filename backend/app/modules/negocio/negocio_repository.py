from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.negocio.negocio_model import Project, StratusGoal, StratusIdea, StratusTask


def list_projects(session: Session) -> list[Project]:
    return list(session.scalars(select(Project).order_by(Project.created_at)))


def project_exists(session: Session, project_id: str) -> bool:
    return session.get(Project, project_id) is not None


def list_tasks(session: Session, project_id: str | None) -> list[StratusTask]:
    query = select(StratusTask).order_by(StratusTask.created_at.desc())
    if project_id is not None:
        query = query.where(StratusTask.project_id == project_id)
    return list(session.scalars(query))


def list_business_ideas(session: Session) -> list[StratusIdea]:
    return list(session.scalars(select(StratusIdea).order_by(StratusIdea.created_at.desc())))


def list_goals(session: Session, month: date) -> list[StratusGoal]:
    query = select(StratusGoal).where(StratusGoal.month == month).order_by(StratusGoal.created_at)
    return list(session.scalars(query))
