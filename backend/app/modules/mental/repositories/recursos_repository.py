from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.mental.models.recursos_model import SkillResource


def list_resources(session: Session) -> list[SkillResource]:
    return list(session.scalars(select(SkillResource).order_by(SkillResource.created_at)))
