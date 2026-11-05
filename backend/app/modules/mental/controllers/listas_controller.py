from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.mental.models.listas_model import ListItem, UserList
from app.modules.mental.schemas.listas_schema import (
    ItemIn,
    ItemMove,
    ItemOut,
    ItemUpdate,
    ListIn,
    ListOut,
    ListSaved,
    ListUpdate,
    ToSkillOut,
)
from app.modules.mental.services import listas_service as service

router = APIRouter()
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/lists", response_model=list[ListOut])
def list_lists(session: SessionDep) -> list[ListOut]:
    return service.list_lists(session)


@router.post("/lists", response_model=ListSaved, status_code=CREATED)
def create_list(payload: ListIn, session: SessionDep) -> UserList:
    return service.create_list(session, payload)


@router.patch("/lists/{list_id}", response_model=ListSaved)
def update_list(list_id: str, payload: ListUpdate, session: SessionDep) -> UserList:
    return service.update_list(session, list_id, payload)


@router.delete("/lists/{list_id}", status_code=NO_CONTENT)
def delete_list(list_id: str, session: SessionDep) -> Response:
    service.delete_list(session, list_id)
    return Response(status_code=NO_CONTENT)


@router.post("/lists/{list_id}/items", response_model=ItemOut, status_code=CREATED)
def add_item(list_id: str, payload: ItemIn, session: SessionDep) -> ListItem:
    return service.add_item(session, list_id, payload)


@router.delete("/lists/{list_id}/done", status_code=NO_CONTENT)
def clear_done(list_id: str, session: SessionDep) -> Response:
    service.clear_done(session, list_id)
    return Response(status_code=NO_CONTENT)


@router.patch("/list-items/{item_id}", response_model=ItemOut)
def update_item(item_id: str, payload: ItemUpdate, session: SessionDep) -> ListItem:
    return service.update_item(session, item_id, payload)


@router.put("/list-items/{item_id}/move", response_model=ItemOut)
def move_item(item_id: str, payload: ItemMove, session: SessionDep) -> ListItem:
    return service.move_item(session, item_id, payload)


@router.post("/list-items/{item_id}/skill", response_model=ToSkillOut, status_code=CREATED)
def item_to_skill(item_id: str, session: SessionDep) -> ToSkillOut:
    return service.item_to_skill(session, item_id)


@router.delete("/list-items/{item_id}", status_code=NO_CONTENT)
def delete_item(item_id: str, session: SessionDep) -> Response:
    service.delete_item(session, item_id)
    return Response(status_code=NO_CONTENT)
