from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mental.models.ideas_model import Idea


def list_ideas(session: Session, tag: str | None) -> list[Idea]:
    query = select(Idea).order_by(Idea.created_at.desc())
    if tag is not None:
        query = query.where(Idea.tag == tag)
    return list(session.scalars(query))


def tag_counts(session: Session) -> list[tuple[str, int]]:
    """Etiquetas en uso, de la más usada a la menos."""
    count = func.count(Idea.id)
    query = select(Idea.tag, count).group_by(Idea.tag).order_by(count.desc(), Idea.tag)
    return [(tag, n) for tag, n in session.execute(query)]
