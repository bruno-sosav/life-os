from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.mental.models.libros_model import Book


def list_books(session: Session) -> list[Book]:
    return list(session.scalars(select(Book).order_by(Book.created_at.desc())))


def books_for_skills(session: Session) -> list[Book]:
    """Los libros vinculados a alguna skill."""
    return list(
        session.scalars(select(Book).where(Book.skill_id.is_not(None)).order_by(Book.title))
    )
