from datetime import date, datetime

from sqlalchemy import CHAR, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, STATUS, Base, CreatedAt, UUIDPk


class StratusTask(UUIDPk, CreatedAt, Base):
    __tablename__ = "stratus_tasks"

    title: Mapped[str] = mapped_column(String(NAME))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(STATUS), default="pendiente", index=True)
    priority: Mapped[str] = mapped_column(String(STATUS), default="media")
    # Toda tarea vive en el tablero de un proyecto: borrar el proyecto borra sus tareas
    project_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer, default=0)  # orden dentro de su columna
    due_date: Mapped[date | None] = mapped_column(Date)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
