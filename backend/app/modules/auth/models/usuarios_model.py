from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import Base, CreatedAt, UUIDPk


class User(UUIDPk, CreatedAt, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    # Se incrementa al cambiar la contraseña: invalida todos los tokens emitidos antes
    token_version: Mapped[int] = mapped_column(Integer, default=0)
