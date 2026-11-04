from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.negocio.models.objetivos_model import StratusGoal
from app.modules.negocio.schemas.objetivos_schema import GoalIn, GoalOut, GoalUpdate
from app.modules.negocio.services import objetivos_service as service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


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
