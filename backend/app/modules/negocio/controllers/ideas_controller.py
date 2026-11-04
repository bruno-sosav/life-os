from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.negocio.models.ideas_model import StratusIdea
from app.modules.negocio.schemas.ideas_schema import BusinessIdeaIn, BusinessIdeaOut
from app.modules.negocio.services import ideas_service as service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/business-ideas", response_model=list[BusinessIdeaOut])
def list_business_ideas(session: SessionDep) -> list[StratusIdea]:
    return service.list_business_ideas(session)


@router.post("/business-ideas", response_model=BusinessIdeaOut, status_code=CREATED)
def create_business_idea(payload: BusinessIdeaIn, session: SessionDep) -> StratusIdea:
    return service.create_business_idea(session, payload)


@router.delete("/business-ideas/{idea_id}", status_code=NO_CONTENT)
def delete_business_idea(idea_id: str, session: SessionDep) -> Response:
    service.delete_business_idea(session, idea_id)
    return Response(status_code=NO_CONTENT)
