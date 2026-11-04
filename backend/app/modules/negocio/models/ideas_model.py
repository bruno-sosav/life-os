from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, Base, CreatedAt, UUIDPk


class StratusIdea(UUIDPk, CreatedAt, Base):
    __tablename__ = "stratus_ideas"

    title: Mapped[str] = mapped_column(String(NAME))
    body: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(JSON)
