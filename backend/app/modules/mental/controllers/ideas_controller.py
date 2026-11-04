from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.ideas_model import Idea
from app.modules.mental.schemas.ideas_schema import IdeaIn, IdeaOut, TagCount
from app.modules.mental.services import ideas_service

router = APIRouter()
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/ideas", response_model=list[IdeaOut])
def list_ideas(session: SessionDep, tag: str | None = None) -> list[Idea]:
    return ideas_service.list_ideas(session, tag)


@router.get("/ideas/tags", response_model=list[TagCount])
def list_tags(session: SessionDep) -> list[TagCount]:
    """Etiquetas en uso, para filtrar y para elegir al cargar una idea."""
    return ideas_service.list_tags(session)


@router.post("/ideas", response_model=IdeaOut, status_code=status.HTTP_201_CREATED)
def create_idea(payload: IdeaIn, session: SessionDep) -> Idea:
    return ideas_service.create_idea(session, payload)


@router.delete("/ideas/{idea_id}", status_code=NO_CONTENT)
def delete_idea(idea_id: str, session: SessionDep) -> Response:
    ideas_service.delete_idea(session, idea_id)
    return Response(status_code=NO_CONTENT)
