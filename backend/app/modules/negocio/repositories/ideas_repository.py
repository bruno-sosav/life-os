from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.negocio.models.ideas_model import StratusIdea


def list_business_ideas(session: Session) -> list[StratusIdea]:
    return list(session.scalars(select(StratusIdea).order_by(StratusIdea.created_at.desc())))
