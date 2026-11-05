from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404, unprocessable
from app.core.fechas_util import week_bounds
from app.modules.mental.models.skills_model import Skill
from app.modules.mental.repositories import (
    libros_repository,
    practicas_repository,
    recursos_repository,
    skills_repository,
)
from app.modules.mental.schemas.recursos_schema import ResourceOut
from app.modules.mental.schemas.skills_schema import (
    BookRef,
    SkillIn,
    SkillOut,
    SkillUpdate,
    WeekMinutes,
)
from app.modules.rutina import Habit

WEEKS = 6  # semanas del mini gráfico de cada skill
STAGE_ORDER = {"practicando": 0, "en_pausa": 1, "la_tengo": 2}


def _check_habit(session: Session, habit_id: str | None) -> None:
    if habit_id is not None and session.get(Habit, habit_id) is None:
        raise unprocessable("El hábito no existe")


def list_skills(session: Session, today: date) -> list[SkillOut]:
    """Cada skill con lo que llevás: la semana de `today`, el total y las últimas 6 semanas.

    Primero las que estás practicando, después las pausadas y al final las que ya tenés.
    """
    mondays = [week_bounds(today, offset).start for offset in range(WEEKS - 1, -1, -1)]
    end = mondays[-1] + timedelta(days=6)
    per_week: dict[tuple[str, date], int] = {}
    for skill_id, day, minutes in practicas_repository.practices_between(session, mondays[0], end):
        key = (skill_id, week_bounds(day).start)
        per_week[key] = per_week.get(key, 0) + minutes
    totals = practicas_repository.totals(session)
    resources = recursos_repository.list_resources(session)
    books = libros_repository.books_for_skills(session)

    skills = sorted(skills_repository.list_skills(session), key=lambda s: STAGE_ORDER[s.stage])
    return [
        SkillOut(
            id=s.id,
            name=s.name,
            type=s.type,
            stage=s.stage,
            weekly_goal_min=s.weekly_goal_min,
            habit_id=s.habit_id,
            week_minutes=per_week.get((s.id, mondays[-1]), 0),
            total_minutes=totals.get(s.id, (0, None))[0],
            last_practice=totals.get(s.id, (0, None))[1],
            weeks=[WeekMinutes(week_start=m, minutes=per_week.get((s.id, m), 0)) for m in mondays],
            resources=[ResourceOut.model_validate(r) for r in resources if r.skill_id == s.id],
            books=[
                BookRef(id=b.id, title=b.title, status=b.status)
                for b in books
                if b.skill_id == s.id
            ],
            created_at=s.created_at,
        )
        for s in skills
    ]


def skill_types(session: Session) -> list[str]:
    return base_repository.used_labels(session, Skill.type)


def create_skill(session: Session, payload: SkillIn) -> Skill:
    _check_habit(session, payload.habit_id)
    return base_repository.save(session, Skill(**payload.model_dump()))


def update_skill(session: Session, skill_id: str, payload: SkillUpdate) -> Skill:
    skill = get_or_404(session, Skill, skill_id)
    changes = payload.model_dump(exclude_unset=True)
    if "habit_id" in changes:
        _check_habit(session, changes["habit_id"])
    return base_repository.save(session, base_repository.apply(skill, changes))


def delete_skill(session: Session, skill_id: str) -> None:
    """Borra la skill con sus prácticas y recursos; los libros vinculados quedan sin skill."""
    base_repository.delete(session, get_or_404(session, Skill, skill_id))
