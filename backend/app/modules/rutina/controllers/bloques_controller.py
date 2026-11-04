from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.rutina.models.bloques_model import RoutineBlock
from app.modules.rutina.schemas.bloques_schema import (
    RoutineBlockIn,
    RoutineBlockOut,
    RoutineCompletionToggle,
)
from app.modules.rutina.services import bloques_service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/routine-blocks/categories", response_model=list[str])
def block_categories(session: SessionDep) -> list[str]:
    return bloques_service.block_categories(session)


@router.post("/routine-blocks", response_model=RoutineBlockOut, status_code=CREATED)
def create_routine_block(payload: RoutineBlockIn, session: SessionDep) -> RoutineBlock:
    return bloques_service.create_routine_block(session, payload)


@router.put("/routine-blocks/{block_id}", response_model=RoutineBlockOut)
def replace_routine_block(
    block_id: str, payload: RoutineBlockIn, session: SessionDep
) -> RoutineBlock:
    return bloques_service.replace_routine_block(session, block_id, payload)


@router.delete("/routine-blocks/{block_id}", status_code=NO_CONTENT)
def delete_routine_block(block_id: str, session: SessionDep) -> Response:
    bloques_service.delete_routine_block(session, block_id)
    return Response(status_code=NO_CONTENT)


@router.put("/routine-completions", status_code=NO_CONTENT)
def toggle_routine_completion(payload: RoutineCompletionToggle, session: SessionDep) -> Response:
    bloques_service.toggle_routine_completion(session, payload)
    return Response(status_code=NO_CONTENT)
