from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.mental.models.ideas_model import Idea
from app.modules.mental.repositories import ideas_repository
from app.modules.mental.schemas.ideas_schema import IdeaIn, TagCount


def list_ideas(session: Session, tag: str | None) -> list[Idea]:
    return ideas_repository.list_ideas(session, tag)


def list_tags(session: Session) -> list[TagCount]:
    return [TagCount(tag=tag, count=n) for tag, n in ideas_repository.tag_counts(session)]


def create_idea(session: Session, payload: IdeaIn) -> Idea:
    return base_repository.save(session, Idea(**payload.model_dump()))


def delete_idea(session: Session, idea_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Idea, idea_id))
