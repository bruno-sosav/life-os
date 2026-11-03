from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.fisico.models.actividades_model import Activity


def list_activities(session: Session, active: bool | None) -> list[Activity]:
    query = select(Activity).order_by(Activity.sort_order, Activity.created_at)
    if active is not None:
        query = query.where(Activity.active == active)
    return list(session.scalars(query))
