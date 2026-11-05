from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel


class ListIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    color: str | None = Field(default=None, max_length=20)
    for_learning: bool = False


class ListUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    color: str | None = Field(default=None, max_length=20)
    for_learning: bool | None = None


class ListSaved(ListIn):
    id: str


class ItemIn(BaseModel):
    text: str = Field(min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=2000)


class ItemUpdate(BaseModel):
    text: str | None = Field(default=None, min_length=1, max_length=255)
    note: str | None = Field(default=None, max_length=2000)
    done: bool | None = None


class ItemMove(BaseModel):
    """Arrastrar un pendiente: queda en `position` entre los pendientes (0 = arriba)."""

    position: int = Field(ge=0)


class ItemOut(ORMModel):
    id: str
    text: str
    note: str | None
    done: bool


class ListOut(ORMModel):
    id: str
    name: str
    color: str | None
    for_learning: bool
    items: list[ItemOut]  # pendientes en su orden, después los hechos


class ToSkillOut(BaseModel):
    skill_id: str
