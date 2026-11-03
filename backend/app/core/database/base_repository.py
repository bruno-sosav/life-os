from collections.abc import Mapping
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import InstrumentedAttribute, Session

from app.core.database.base_model import Base


def save[T: Base](session: Session, record: T) -> T:
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete(session: Session, record: Base) -> None:
    session.delete(record)
    session.commit()


def apply[T: Base](record: T, changes: Mapping[str, Any]) -> T:
    """Copia `changes` (campo → valor) sobre el registro. No guarda: para eso está save."""
    for field, value in changes.items():
        setattr(record, field, value)
    return record


def used_labels(session: Session, column: InstrumentedAttribute[str | None]) -> list[str]:
    """Valores distintos de `column` en uso, del más usado al menos."""
    count = func.count()
    query = (
        select(column).where(column.is_not(None)).group_by(column).order_by(count.desc(), column)
    )
    return [value for value in session.scalars(query) if value]
