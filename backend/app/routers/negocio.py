from datetime import UTC, date, datetime

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database.conexion_database import SessionDep
from app.core.errores_util import get_or_404
from app.models import Project, StratusGoal, StratusIdea, StratusTask
from app.schemas.negocio import (
    BusinessIdeaIn,
    BusinessIdeaOut,
    GoalIn,
    GoalOut,
    GoalUpdate,
    ProjectIn,
    ProjectOut,
    TaskIn,
    TaskOut,
    TaskUpdate,
)

router = APIRouter(tags=["negocio"])


def _first_of_month(day: date) -> date:
    return day.replace(day=1)


def _check_project(session: Session, project_id: str | None) -> None:
    if project_id is not None and session.get(Project, project_id) is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "El proyecto no existe")


def _sync_completed_at(task: StratusTask) -> None:
    """completed_at se marca al pasar a 'hecho' y se limpia al salir."""
    if task.status == "hecho":
        task.completed_at = task.completed_at or datetime.now(UTC).replace(tzinfo=None)
    else:
        task.completed_at = None


# ─── Proyectos ──────────────────────────────────────────────
@router.get("/projects", response_model=list[ProjectOut])
def list_projects(session: SessionDep) -> list[Project]:
    return list(session.scalars(select(Project).order_by(Project.created_at)))


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectIn, session: SessionDep) -> Project:
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, session: SessionDep) -> Response:
    """Las tareas del proyecto quedan sin proyecto (ON DELETE SET NULL)."""
    session.delete(get_or_404(session, Project, project_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Tareas ─────────────────────────────────────────────────
@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(session: SessionDep, project_id: str | None = None) -> list[StratusTask]:
    query = select(StratusTask).order_by(StratusTask.created_at.desc())
    if project_id is not None:
        query = query.where(StratusTask.project_id == project_id)
    return list(session.scalars(query))


@router.post("/tasks", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskIn, session: SessionDep) -> StratusTask:
    _check_project(session, payload.project_id)
    task = StratusTask(**payload.model_dump())
    _sync_completed_at(task)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, session: SessionDep) -> StratusTask:
    task = get_or_404(session, StratusTask, task_id)
    changes = payload.model_dump(exclude_unset=True)
    if "project_id" in changes:
        _check_project(session, changes["project_id"])
    for field, value in changes.items():
        setattr(task, field, value)
    _sync_completed_at(task)
    session.commit()
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, StratusTask, task_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Ideas de negocio ───────────────────────────────────────
@router.get("/business-ideas", response_model=list[BusinessIdeaOut])
def list_business_ideas(session: SessionDep) -> list[StratusIdea]:
    return list(session.scalars(select(StratusIdea).order_by(StratusIdea.created_at.desc())))


@router.post("/business-ideas", response_model=BusinessIdeaOut, status_code=status.HTTP_201_CREATED)
def create_business_idea(payload: BusinessIdeaIn, session: SessionDep) -> StratusIdea:
    idea = StratusIdea(**payload.model_dump())
    session.add(idea)
    session.commit()
    session.refresh(idea)
    return idea


@router.delete("/business-ideas/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_idea(idea_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, StratusIdea, idea_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Objetivos del mes ──────────────────────────────────────
@router.get("/goals", response_model=list[GoalOut])
def list_goals(month: date, session: SessionDep) -> list[StratusGoal]:
    query = (
        select(StratusGoal)
        .where(StratusGoal.month == _first_of_month(month))
        .order_by(StratusGoal.created_at)
    )
    return list(session.scalars(query))


@router.post("/goals", response_model=GoalOut, status_code=status.HTTP_201_CREATED)
def create_goal(payload: GoalIn, session: SessionDep) -> StratusGoal:
    goal = StratusGoal(title=payload.title, month=_first_of_month(payload.month), progress=0)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.patch("/goals/{goal_id}", response_model=GoalOut)
def update_goal(goal_id: str, payload: GoalUpdate, session: SessionDep) -> StratusGoal:
    goal = get_or_404(session, StratusGoal, goal_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    goal.completed = goal.progress >= 100
    session.commit()
    return goal


@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, StratusGoal, goal_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
