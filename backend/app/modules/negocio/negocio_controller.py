from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.negocio import negocio_service as service
from app.modules.negocio.negocio_model import Project, StratusGoal, StratusIdea, StratusTask
from app.modules.negocio.negocio_schema import (
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
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(session: SessionDep) -> list[Project]:
    return service.list_projects(session)


@router.post("/projects", response_model=ProjectOut, status_code=CREATED)
def create_project(payload: ProjectIn, session: SessionDep) -> Project:
    return service.create_project(session, payload)


@router.delete("/projects/{project_id}", status_code=NO_CONTENT)
def delete_project(project_id: str, session: SessionDep) -> Response:
    service.delete_project(session, project_id)
    return Response(status_code=NO_CONTENT)


@router.get("/tasks", response_model=list[TaskOut])
def list_tasks(session: SessionDep, project_id: str | None = None) -> list[StratusTask]:
    return service.list_tasks(session, project_id)


@router.post("/tasks", response_model=TaskOut, status_code=CREATED)
def create_task(payload: TaskIn, session: SessionDep) -> StratusTask:
    return service.create_task(session, payload)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, session: SessionDep) -> StratusTask:
    return service.update_task(session, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=NO_CONTENT)
def delete_task(task_id: str, session: SessionDep) -> Response:
    service.delete_task(session, task_id)
    return Response(status_code=NO_CONTENT)


@router.get("/business-ideas", response_model=list[BusinessIdeaOut])
def list_business_ideas(session: SessionDep) -> list[StratusIdea]:
    return service.list_business_ideas(session)


@router.post("/business-ideas", response_model=BusinessIdeaOut, status_code=CREATED)
def create_business_idea(payload: BusinessIdeaIn, session: SessionDep) -> StratusIdea:
    return service.create_business_idea(session, payload)


@router.delete("/business-ideas/{idea_id}", status_code=NO_CONTENT)
def delete_business_idea(idea_id: str, session: SessionDep) -> Response:
    service.delete_business_idea(session, idea_id)
    return Response(status_code=NO_CONTENT)


@router.get("/goals", response_model=list[GoalOut])
def list_goals(month: date, session: SessionDep) -> list[StratusGoal]:
    return service.list_goals(session, month)


@router.post("/goals", response_model=GoalOut, status_code=CREATED)
def create_goal(payload: GoalIn, session: SessionDep) -> StratusGoal:
    return service.create_goal(session, payload)


@router.patch("/goals/{goal_id}", response_model=GoalOut)
def update_goal(goal_id: str, payload: GoalUpdate, session: SessionDep) -> StratusGoal:
    return service.update_goal(session, goal_id, payload)


@router.delete("/goals/{goal_id}", status_code=NO_CONTENT)
def delete_goal(goal_id: str, session: SessionDep) -> Response:
    service.delete_goal(session, goal_id)
    return Response(status_code=NO_CONTENT)
