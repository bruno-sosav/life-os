from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.mental.models.recursos_model import SkillResource
from app.modules.mental.models.skills_model import Skill
from app.modules.mental.schemas.recursos_schema import ResourceIn


def create_resource(session: Session, skill_id: str, payload: ResourceIn) -> SkillResource:
    get_or_404(session, Skill, skill_id)
    return base_repository.save(session, SkillResource(skill_id=skill_id, **payload.model_dump()))


def delete_resource(session: Session, resource_id: str) -> None:
    base_repository.delete(session, get_or_404(session, SkillResource, resource_id))
