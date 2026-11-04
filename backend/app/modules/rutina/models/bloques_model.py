from datetime import date, datetime

from sqlalchemy import (
    CHAR,
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, EMOJI, NAME, Base, CreatedAt, UUIDPk


class RoutineBlock(UUIDPk, CreatedAt, Base):
    __tablename__ = "routine_blocks"

    # días en que se repite (0 = lunes … 6 = domingo); null si es de fecha puntual
    days_of_week: Mapped[list[int] | None] = mapped_column(JSON)
    specific_date: Mapped[date | None] = mapped_column(Date)
    repeat_weekly: Mapped[bool] = mapped_column(Boolean, default=True)
    hour_start: Mapped[int] = mapped_column(Integer)
    hour_min: Mapped[int] = mapped_column(Integer, default=0)
    hour_end: Mapped[int] = mapped_column(Integer)
    activity: Mapped[str] = mapped_column(String(NAME))
    category: Mapped[str | None] = mapped_column(String(30))
    emoji: Mapped[str | None] = mapped_column(String(EMOJI))
    color: Mapped[str | None] = mapped_column(String(COLOR))


class RoutineCompletion(UUIDPk, Base):
    __tablename__ = "routine_completions"
    __table_args__ = (UniqueConstraint("block_id", "date"),)

    block_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("routine_blocks.id", ondelete="CASCADE")
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
