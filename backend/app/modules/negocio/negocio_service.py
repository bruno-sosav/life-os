from datetime import UTC, date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import month_bounds
from app.modules.negocio import negocio_repository as repository
from app.modules.negocio.negocio_model import Project, StratusGoal, StratusIdea, StratusTask
from app.modules.negocio.negocio_schema import (
    BusinessIdeaIn,
    GoalIn,
    GoalUpdate,
    ProjectIn,
    TaskIn,
    TaskUpdate,
)


def _check_project(session: Session, project_id: str | None) -> None:
    if project_id is not None and not repository.project_exists(session, project_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "El proyecto no existe")


def _sync_completed_at(task: StratusTask) -> None:
    """completed_at se marca al pasar a 'hecho' y se limpia al salir."""
    if task.status == "hecho":
        task.completed_at = task.completed_at or datetime.now(UTC).replace(tzinfo=None)
    else:
        task.completed_at = None


# ─── Proyectos ──────────────────────────────────────────────
def list_projects(session: Session) -> list[Project]:
    return repository.list_projects(session)


def create_project(session: Session, payload: ProjectIn) -> Project:
    return base_repository.save(session, Project(**payload.model_dump()))


def delete_project(session: Session, project_id: str) -> None:
    """Las tareas del proyecto quedan sin proyecto (ON DELETE SET NULL)."""
    base_repository.delete(session, get_or_404(session, Project, project_id))


# ─── Tareas ─────────────────────────────────────────────────
def list_tasks(session: Session, project_id: str | None) -> list[StratusTask]:
    return repository.list_tasks(session, project_id)


def create_task(session: Session, payload: TaskIn) -> StratusTask:
    _check_project(session, payload.project_id)
    task = StratusTask(**payload.model_dump())
    _sync_completed_at(task)
    return base_repository.save(session, task)


def update_task(session: Session, task_id: str, payload: TaskUpdate) -> StratusTask:
    task = get_or_404(session, StratusTask, task_id)
    changes = payload.model_dump(exclude_unset=True)
    if "project_id" in changes:
        _check_project(session, changes["project_id"])
    _sync_completed_at(base_repository.apply(task, changes))
    return base_repository.save(session, task)


def delete_task(session: Session, task_id: str) -> None:
    base_repository.delete(session, get_or_404(session, StratusTask, task_id))


# ─── Ideas de negocio ───────────────────────────────────────
def list_business_ideas(session: Session) -> list[StratusIdea]:
    return repository.list_business_ideas(session)


def create_business_idea(session: Session, payload: BusinessIdeaIn) -> StratusIdea:
    return base_repository.save(session, StratusIdea(**payload.model_dump()))


def delete_business_idea(session: Session, idea_id: str) -> None:
    base_repository.delete(session, get_or_404(session, StratusIdea, idea_id))


# ─── Objetivos del mes ──────────────────────────────────────
def list_goals(session: Session, month: date) -> list[StratusGoal]:
    return repository.list_goals(session, month_bounds(month).start)


def create_goal(session: Session, payload: GoalIn) -> StratusGoal:
    goal = StratusGoal(title=payload.title, month=month_bounds(payload.month).start, progress=0)
    return base_repository.save(session, goal)


def update_goal(session: Session, goal_id: str, payload: GoalUpdate) -> StratusGoal:
    goal = base_repository.apply(
        get_or_404(session, StratusGoal, goal_id), payload.model_dump(exclude_unset=True)
    )
    goal.completed = goal.progress >= 100
    return base_repository.save(session, goal)


def delete_goal(session: Session, goal_id: str) -> None:
    base_repository.delete(session, get_or_404(session, StratusGoal, goal_id))
