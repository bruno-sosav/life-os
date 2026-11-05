from sqlalchemy import CHAR, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import COLOR, NAME, Base, CreatedAt, UUIDPk


class UserList(UUIDPk, CreatedAt, Base):
    """Una lista libre: compras, películas, cosas para aprender…"""

    __tablename__ = "user_lists"

    name: Mapped[str] = mapped_column(String(NAME))
    color: Mapped[str | None] = mapped_column(String(COLOR))
    # "Es para aprender": sus ítems se pueden pasar a skills
    for_learning: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)


class ListItem(UUIDPk, CreatedAt, Base):
    __tablename__ = "list_items"

    list_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("user_lists.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(String(NAME))
    note: Mapped[str | None] = mapped_column(Text)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)  # orden entre los pendientes
