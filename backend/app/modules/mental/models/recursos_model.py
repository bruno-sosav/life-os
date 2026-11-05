from sqlalchemy import CHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, STATUS, Base, CreatedAt, UUIDPk


class SkillResource(UUIDPk, CreatedAt, Base):
    """Un curso, libro, link o video para aprender una skill."""

    __tablename__ = "skill_resources"

    skill_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("skills.id", ondelete="CASCADE"), index=True
    )
    kind: Mapped[str] = mapped_column(String(STATUS))
    name: Mapped[str] = mapped_column(String(NAME))
    url: Mapped[str | None] = mapped_column(String(500))
