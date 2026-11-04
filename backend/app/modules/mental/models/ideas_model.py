from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, STATUS, Base, CreatedAt, UUIDPk


class Idea(UUIDPk, CreatedAt, Base):
    __tablename__ = "ideas"

    text: Mapped[str] = mapped_column(Text)
    author: Mapped[str | None] = mapped_column(String(NAME))
    # Etiqueta libre, se muestra tal cual ("💬 Frase", "📚 Aprendizaje"…)
    tag: Mapped[str] = mapped_column(String(STATUS), default="💡 Idea")
