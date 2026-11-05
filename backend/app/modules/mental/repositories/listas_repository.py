from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.mental.models.listas_model import ListItem, UserList


def list_lists(session: Session) -> list[UserList]:
    return list(session.scalars(select(UserList).order_by(UserList.position, UserList.created_at)))


def items_of(session: Session, list_id: str | None = None) -> list[ListItem]:
    """Ítems en orden: pendientes por su lugar, después los hechos. Sin `list_id`, de todas."""
    query = select(ListItem).order_by(ListItem.done, ListItem.position, ListItem.created_at)
    if list_id is not None:
        query = query.where(ListItem.list_id == list_id)
    return list(session.scalars(query))


def next_list_position(session: Session) -> int:
    last = session.scalar(select(func.max(UserList.position)))
    return 0 if last is None else int(last) + 1


def first_item_position(session: Session, list_id: str) -> int:
    """Un lugar arriba del primer pendiente: lo nuevo entra arriba de todo."""
    query = select(func.min(ListItem.position)).where(
        ListItem.list_id == list_id, ListItem.done.is_(False)
    )
    first = session.scalar(query)
    return 0 if first is None else int(first) - 1
