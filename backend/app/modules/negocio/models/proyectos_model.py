from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, EMOJI, NAME, Base, CreatedAt, UUIDPk


class Project(UUIDPk, CreatedAt, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(NAME))
    color: Mapped[str | None] = mapped_column(String(COLOR), default="#0A84FF")
    emoji: Mapped[str | None] = mapped_column(String(EMOJI), default="📁")
    description: Mapped[str | None] = mapped_column(Text)
