from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.negocio.models.ideas_model import StratusIdea
from app.modules.negocio.repositories import ideas_repository
from app.modules.negocio.schemas.ideas_schema import BusinessIdeaIn


def list_business_ideas(session: Session) -> list[StratusIdea]:
    return ideas_repository.list_business_ideas(session)


def create_business_idea(session: Session, payload: BusinessIdeaIn) -> StratusIdea:
    return base_repository.save(session, StratusIdea(**payload.model_dump()))


def delete_business_idea(session: Session, idea_id: str) -> None:
    base_repository.delete(session, get_or_404(session, StratusIdea, idea_id))
