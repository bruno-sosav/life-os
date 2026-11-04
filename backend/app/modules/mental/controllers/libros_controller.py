from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.libros_model import Book
from app.modules.mental.schemas.libros_schema import BookIn, BookOut, BookUpdate, Library
from app.modules.mental.services import libros_service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/books/library", response_model=Library)
def library(today: date, session: SessionDep) -> Library:
    """Estantes (pendiente, leyendo, leído) y libros leídos en el año."""
    return libros_service.library(session, today)


@router.post("/books", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(payload: BookIn, session: SessionDep) -> Book:
    return libros_service.create_book(session, payload)


@router.patch("/books/{book_id}", response_model=BookOut)
def update_book(book_id: str, payload: BookUpdate, session: SessionDep) -> Book:
    return libros_service.update_book(session, book_id, payload)


@router.delete("/books/{book_id}", status_code=NO_CONTENT)
def delete_book(book_id: str, session: SessionDep) -> Response:
    libros_service.delete_book(session, book_id)
    return Response(status_code=NO_CONTENT)
