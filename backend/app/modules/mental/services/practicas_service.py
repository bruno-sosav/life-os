from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404, unprocessable
from app.modules.mental.models.practicas_model import Practice
from app.modules.mental.models.skills_model import Skill
from app.modules.mental.repositories import practicas_repository
from app.modules.mental.schemas.practicas_schema import PracticeIn
from app.modules.rutina import mark_linked_habit


def list_practices(session: Session, skill_id: str, limit: int) -> list[Practice]:
    get_or_404(session, Skill, skill_id)
    return practicas_repository.list_practices(session, skill_id, limit)


def create_practice(session: Session, payload: PracticeIn) -> Practice:
    """Registra la práctica y, con hábito vinculado, lo marca cumplido ese día."""
    skill = session.get(Skill, payload.skill_id)
    if skill is None:
        raise unprocessable("La skill no existe")
    practice = base_repository.save(session, Practice(**payload.model_dump()))
    mark_linked_habit(session, skill.habit_id, practice.date, done=True)
    return practice


def delete_practice(session: Session, practice_id: str) -> None:
    """Borrar la única práctica de ese día desmarca el hábito vinculado."""
    practice = get_or_404(session, Practice, practice_id)
    skill = get_or_404(session, Skill, practice.skill_id)
    day: date = practice.date
    base_repository.delete(session, practice)
    done = practicas_repository.practiced_on(session, skill.id, day) > 0
    mark_linked_habit(session, skill.habit_id, day, done)
