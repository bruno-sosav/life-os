from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.mental.models.listas_model import ListItem, UserList
from app.modules.mental.models.skills_model import Skill
from app.modules.mental.repositories import listas_repository
from app.modules.mental.schemas.listas_schema import (
    ItemIn,
    ItemMove,
    ItemOut,
    ItemUpdate,
    ListIn,
    ListOut,
    ListUpdate,
    ToSkillOut,
)


def list_lists(session: Session) -> list[ListOut]:
    """Todas las listas con sus ítems: pendientes en su orden, después los hechos."""
    items = listas_repository.items_of(session)
    return [
        ListOut(
            id=lst.id,
            name=lst.name,
            color=lst.color,
            for_learning=lst.for_learning,
            items=[ItemOut.model_validate(i) for i in items if i.list_id == lst.id],
        )
        for lst in listas_repository.list_lists(session)
    ]


def create_list(session: Session, payload: ListIn) -> UserList:
    position = listas_repository.next_list_position(session)
    return base_repository.save(session, UserList(**payload.model_dump(), position=position))


def update_list(session: Session, list_id: str, payload: ListUpdate) -> UserList:
    lst = get_or_404(session, UserList, list_id)
    return base_repository.save(
        session, base_repository.apply(lst, payload.model_dump(exclude_unset=True))
    )


def delete_list(session: Session, list_id: str) -> None:
    """Borra la lista con todos sus ítems."""
    base_repository.delete(session, get_or_404(session, UserList, list_id))


def add_item(session: Session, list_id: str, payload: ItemIn) -> ListItem:
    """Lo nuevo entra arriba de todo."""
    get_or_404(session, UserList, list_id)
    position = listas_repository.first_item_position(session, list_id)
    return base_repository.save(
        session, ListItem(list_id=list_id, position=position, **payload.model_dump())
    )


def update_item(session: Session, item_id: str, payload: ItemUpdate) -> ListItem:
    item = get_or_404(session, ListItem, item_id)
    return base_repository.save(
        session, base_repository.apply(item, payload.model_dump(exclude_unset=True))
    )


def move_item(session: Session, item_id: str, payload: ItemMove) -> ListItem:
    """Arrastrar un pendiente: queda en `position` y los demás pendientes se corren."""
    item = get_or_404(session, ListItem, item_id)
    pending = [
        i
        for i in listas_repository.items_of(session, item.list_id)
        if not i.done and i.id != item.id
    ]
    pending.insert(min(payload.position, len(pending)), item)
    for position, row in enumerate(pending):
        row.position = position
    return base_repository.save(session, item)


def delete_item(session: Session, item_id: str) -> None:
    base_repository.delete(session, get_or_404(session, ListItem, item_id))


def clear_done(session: Session, list_id: str) -> None:
    """Borra los ítems tachados de la lista."""
    get_or_404(session, UserList, list_id)
    for item in listas_repository.items_of(session, list_id):
        if item.done:
            session.delete(item)
    session.commit()


def item_to_skill(session: Session, item_id: str) -> ToSkillOut:
    """ "Practicar →": el ítem pasa a ser una skill que estás practicando y queda tachado."""
    item = get_or_404(session, ListItem, item_id)
    skill = Skill(name=item.text, stage="practicando")
    item.done = True
    session.add(skill)
    base_repository.save(session, item)
    return ToSkillOut(skill_id=skill.id)
