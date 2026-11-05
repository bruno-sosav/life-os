from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.mental.models.skills_model import Skill


def list_skills(session: Session) -> list[Skill]:
    return list(session.scalars(select(Skill).order_by(Skill.created_at)))
