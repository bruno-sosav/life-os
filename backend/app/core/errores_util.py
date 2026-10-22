from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.database.base_model import Base


def get_or_404[T: Base](session: Session, model: type[T], id_: str) -> T:
    obj = session.get(model, id_)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{model.__name__} {id_} no existe")
    return obj
