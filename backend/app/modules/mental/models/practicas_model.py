from datetime import date

from sqlalchemy import CHAR, CheckConstraint, Date, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import Base, CreatedAt, UUIDPk


class Practice(UUIDPk, CreatedAt, Base):
    __tablename__ = "skill_practices"
    __table_args__ = (CheckConstraint("minutes > 0", name="minutes"),)

    skill_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("skills.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    minutes: Mapped[int] = mapped_column(Integer)
    note: Mapped[str | None] = mapped_column(Text)
