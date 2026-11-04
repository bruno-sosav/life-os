from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.mental.models.libros_model import Book


def list_books(session: Session) -> list[Book]:
    return list(session.scalars(select(Book).order_by(Book.created_at.desc())))
