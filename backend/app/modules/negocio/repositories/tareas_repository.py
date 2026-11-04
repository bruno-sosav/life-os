from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.negocio.models.tareas_model import StratusTask


def list_tasks(session: Session, project_id: str) -> list[StratusTask]:
    query = (
        select(StratusTask)
        .where(StratusTask.project_id == project_id)
        .order_by(StratusTask.position, StratusTask.created_at)
    )
    return list(session.scalars(query))


def column_tasks(session: Session, project_id: str, status: str) -> list[StratusTask]:
    """Las tareas de una columna del tablero, en su orden."""
    query = (
        select(StratusTask)
        .where(StratusTask.project_id == project_id, StratusTask.status == status)
        .order_by(StratusTask.position, StratusTask.created_at)
    )
    return list(session.scalars(query))
