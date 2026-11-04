from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.negocio.models.tareas_model import StratusTask
from app.modules.negocio.schemas.tareas_schema import Board, TaskIn, TaskMove, TaskOut, TaskUpdate
from app.modules.negocio.services import tareas_service as service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/tasks/board", response_model=Board)
def task_board(project_id: str, session: SessionDep) -> dict[str, list[StratusTask]]:
    return service.board(session, project_id)


@router.post("/tasks", response_model=TaskOut, status_code=CREATED)
def create_task(payload: TaskIn, session: SessionDep) -> StratusTask:
    return service.create_task(session, payload)


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: str, payload: TaskUpdate, session: SessionDep) -> StratusTask:
    return service.update_task(session, task_id, payload)


@router.put("/tasks/{task_id}/move", response_model=TaskOut)
def move_task(task_id: str, payload: TaskMove, session: SessionDep) -> StratusTask:
    return service.move_task(session, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=NO_CONTENT)
def delete_task(task_id: str, session: SessionDep) -> Response:
    service.delete_task(session, task_id)
    return Response(status_code=NO_CONTENT)
