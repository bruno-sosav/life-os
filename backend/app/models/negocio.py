from datetime import date, datetime

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, EMOJI, NAME, STATUS, Base, CreatedAt, UUIDPk


class Project(UUIDPk, CreatedAt, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(NAME))
    color: Mapped[str | None] = mapped_column(String(COLOR), default="#0A84FF")
    emoji: Mapped[str | None] = mapped_column(String(EMOJI), default="📁")
    description: Mapped[str | None] = mapped_column(Text)


class StratusTask(UUIDPk, CreatedAt, Base):
    __tablename__ = "stratus_tasks"

    title: Mapped[str] = mapped_column(String(NAME))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(STATUS), default="pendiente", index=True)
    priority: Mapped[str] = mapped_column(String(STATUS), default="media")
    project_id: Mapped[str | None] = mapped_column(
        CHAR(36), ForeignKey("projects.id", ondelete="SET NULL"), index=True
    )
    due_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)


class StratusIdea(UUIDPk, CreatedAt, Base):
    __tablename__ = "stratus_ideas"

    title: Mapped[str] = mapped_column(String(NAME))
    body: Mapped[str | None] = mapped_column(Text)
    tags: Mapped[list[str] | None] = mapped_column(JSON)


class StratusGoal(UUIDPk, CreatedAt, Base):
    __tablename__ = "stratus_goals"
    __table_args__ = (CheckConstraint("progress BETWEEN 0 AND 100", name="progress"),)

    month: Mapped[date] = mapped_column(Date, index=True)  # primer día del mes
    title: Mapped[str] = mapped_column(String(NAME))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
