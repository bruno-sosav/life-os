from sqlalchemy import CHAR, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.common import COLOR, EMOJI, NAME, STATUS, CreatedAt, UUIDPk


class PersonalList(UUIDPk, CreatedAt, Base):
    __tablename__ = "personal_lists"

    name: Mapped[str] = mapped_column(String(NAME))
    color: Mapped[str | None] = mapped_column(String(COLOR), default="#30D158")
    icon: Mapped[str | None] = mapped_column(String(EMOJI))


class ListItem(UUIDPk, CreatedAt, Base):
    __tablename__ = "list_items"

    list_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("personal_lists.id", ondelete="CASCADE"), index=True
    )
    text: Mapped[str] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(STATUS), default="pendiente")
    checked: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=0)
