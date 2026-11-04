from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.core.fechas_util import month_bounds
from app.modules.negocio.models.objetivos_model import StratusGoal
from app.modules.negocio.repositories import objetivos_repository
from app.modules.negocio.schemas.objetivos_schema import GoalIn, GoalUpdate


def list_goals(session: Session, month: date) -> list[StratusGoal]:
    return objetivos_repository.list_goals(session, month_bounds(month).start)


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
