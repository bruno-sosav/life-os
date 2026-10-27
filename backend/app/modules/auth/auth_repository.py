from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.auth_model import User


def user_by_username(session: Session, username: str) -> User | None:
    return session.scalar(select(User).where(User.username == username))


def user_by_id(session: Session, user_id: str) -> User | None:
    return session.get(User, user_id)
