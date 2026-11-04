from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.mental.models.libros_model import Book
from app.modules.mental.repositories import libros_repository
from app.modules.mental.schemas.libros_schema import BookIn, BookUpdate, Library, Shelves


def library(session: Session, today: date) -> Library:
    """Los libros agrupados por estante y cuántos se terminaron en el año de `today`."""
    books = libros_repository.list_books(session)
    read = [b for b in books if b.status == "leido"]
    return Library(
        shelves=Shelves.model_validate(
            {status: [b for b in books if b.status == status] for status in Shelves.model_fields}
        ),
        year=today.year,
        read_this_year=sum(1 for b in read if b.finished_at and b.finished_at.year == today.year),
    )


def create_book(session: Session, payload: BookIn) -> Book:
    return base_repository.save(session, Book(**payload.model_dump()))


def update_book(session: Session, book_id: str, payload: BookUpdate) -> Book:
    book = get_or_404(session, Book, book_id)
    return base_repository.save(
        session, base_repository.apply(book, payload.model_dump(exclude_unset=True))
    )


def delete_book(session: Session, book_id: str) -> None:
    base_repository.delete(session, get_or_404(session, Book, book_id))
