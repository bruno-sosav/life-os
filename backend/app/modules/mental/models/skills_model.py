from sqlalchemy import CHAR, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, STATUS, Base, CreatedAt, UUIDPk


class Skill(UUIDPk, CreatedAt, Base):
    """Algo que querés aprender o practicar: un idioma, ajedrez, ventas…"""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(String(NAME))
    # Etiqueta libre, se muestra tal cual ("Idioma", "Hobby"…)
    type: Mapped[str | None] = mapped_column(String(STATUS))
    stage: Mapped[str] = mapped_column(String(STATUS), default="practicando")
    weekly_goal_min: Mapped[int | None] = mapped_column(Integer)  # meta de la semana, en minutos
    # Con hábito vinculado, registrar una práctica lo marca cumplido ese día
    habit_id: Mapped[str | None] = mapped_column(
        CHAR(36), ForeignKey("habits.id", ondelete="SET NULL")
    )
