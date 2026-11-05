from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.skills_model import Skill
from app.modules.mental.schemas.skills_schema import SkillCreated, SkillIn, SkillOut, SkillUpdate
from app.modules.mental.services import skills_service as service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/skills", response_model=list[SkillOut])
def list_skills(today: date, session: SessionDep) -> list[SkillOut]:
    return service.list_skills(session, today)


@router.get("/skills/types", response_model=list[str])
def skill_types(session: SessionDep) -> list[str]:
    return service.skill_types(session)


@router.post("/skills", response_model=SkillCreated, status_code=status.HTTP_201_CREATED)
def create_skill(payload: SkillIn, session: SessionDep) -> Skill:
    return service.create_skill(session, payload)


@router.patch("/skills/{skill_id}", response_model=SkillCreated)
def update_skill(skill_id: str, payload: SkillUpdate, session: SessionDep) -> Skill:
    return service.update_skill(session, skill_id, payload)


@router.delete("/skills/{skill_id}", status_code=NO_CONTENT)
def delete_skill(skill_id: str, session: SessionDep) -> Response:
    service.delete_skill(session, skill_id)
    return Response(status_code=NO_CONTENT)
