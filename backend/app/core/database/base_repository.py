from sqlalchemy.orm import Session

from app.core.database.base_model import Base


def save[T: Base](session: Session, record: T) -> T:
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


def delete(session: Session, record: Base) -> None:
    session.delete(record)
    session.commit()
