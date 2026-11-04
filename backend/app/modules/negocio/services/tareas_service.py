from datetime import UTC, datetime
from typing import get_args

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404, unprocessable
from app.modules.negocio.models.tareas_model import StratusTask
from app.modules.negocio.repositories import proyectos_repository, tareas_repository
from app.modules.negocio.schemas.tareas_schema import TaskIn, TaskMove, TaskStatus, TaskUpdate


def _check_project(session: Session, project_id: str | None) -> None:
    if project_id is None or not proyectos_repository.project_exists(session, project_id):
        raise unprocessable("El proyecto no existe")


def _sync_completed_at(task: StratusTask) -> None:
    """completed_at se marca al pasar a 'hecho' y se limpia al salir."""
    if task.status == "hecho":
        task.completed_at = task.completed_at or datetime.now(UTC).replace(tzinfo=None)
    else:
        task.completed_at = None


def _last_position(session: Session, project_id: str, status: str) -> int:
    """Lugar para una tarea que entra a una columna: al final."""
    column = tareas_repository.column_tasks(session, project_id, status)
    return column[-1].position + 1 if column else 0


def board(session: Session, project_id: str) -> dict[str, list[StratusTask]]:
    """El tablero del proyecto: sus tareas por columna, en el orden en que las dejaste."""
    _check_project(session, project_id)
    columns: dict[str, list[StratusTask]] = {s: [] for s in get_args(TaskStatus)}
    for task in tareas_repository.list_tasks(session, project_id):
        columns[task.status].append(task)
    return columns


def create_task(session: Session, payload: TaskIn) -> StratusTask:
    _check_project(session, payload.project_id)
    task = StratusTask(
        **payload.model_dump(),
        position=_last_position(session, payload.project_id, payload.status),
    )
    _sync_completed_at(task)
    return base_repository.save(session, task)


def update_task(session: Session, task_id: str, payload: TaskUpdate) -> StratusTask:
    """Editar desde el formulario. Si cambia de columna o de proyecto, va al final de la nueva."""
    task = get_or_404(session, StratusTask, task_id)
    changes = payload.model_dump(exclude_unset=True)
    if "project_id" in changes:
        _check_project(session, changes["project_id"])
    column = (task.project_id, task.status)
    base_repository.apply(task, changes)
    if (task.project_id, task.status) != column:
        task.position = _last_position(session, task.project_id, task.status)
    _sync_completed_at(task)
    return base_repository.save(session, task)


def move_task(session: Session, task_id: str, payload: TaskMove) -> StratusTask:
    """Arrastrar: la tarea queda en `position` de la columna `status` y el resto se corre.

    Se renumera solo la columna de destino: en la de origen queda un hueco, que no
    cambia el orden.
    """
    task = get_or_404(session, StratusTask, task_id)
    column = [
        t
        for t in tareas_repository.column_tasks(session, task.project_id, payload.status)
        if t.id != task.id
    ]
    column.insert(min(payload.position, len(column)), task)
    task.status = payload.status
    for position, item in enumerate(column):
        item.position = position
    _sync_completed_at(task)
    return base_repository.save(session, task)


def delete_task(session: Session, task_id: str) -> None:
    base_repository.delete(session, get_or_404(session, StratusTask, task_id))
