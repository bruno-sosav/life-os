from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mental.models.practicas_model import Practice


def practices_between(session: Session, start: date, end: date) -> list[tuple[str, date, int]]:
    """(skill_id, fecha, minutos) de cada práctica del rango, de cualquier skill."""
    query = select(Practice.skill_id, Practice.date, Practice.minutes).where(
        Practice.date.between(start, end)
    )
    return [(skill_id, day, minutes) for skill_id, day, minutes in session.execute(query)]


def totals(session: Session) -> dict[str, tuple[int, date]]:
    """Por skill: minutos de toda la historia y la última fecha practicada."""
    query = select(Practice.skill_id, func.sum(Practice.minutes), func.max(Practice.date)).group_by(
        Practice.skill_id
    )
    return {skill_id: (int(total), last) for skill_id, total, last in session.execute(query)}


def list_practices(session: Session, skill_id: str, limit: int) -> list[Practice]:
    query = (
        select(Practice)
        .where(Practice.skill_id == skill_id)
        .order_by(Practice.date.desc(), Practice.created_at.desc())
        .limit(limit)
    )
    return list(session.scalars(query))


def practiced_on(session: Session, skill_id: str, day: date) -> int:
    """Cuántas prácticas tiene la skill ese día."""
    query = select(func.count()).where(Practice.skill_id == skill_id, Practice.date == day)
    return int(session.scalar(query) or 0)
