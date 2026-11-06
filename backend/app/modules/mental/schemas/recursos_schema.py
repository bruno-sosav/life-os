from typing import Literal

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel

ResourceKind = Literal["curso", "libro", "link", "video", "otro"]


class ResourceIn(BaseModel):
    kind: ResourceKind = "link"
    name: str = Field(min_length=1, max_length=255)
    # Solo http(s): el link se abre en la app y un "javascript:…" ejecutaría código
    url: str | None = Field(default=None, max_length=500, pattern=r"^(?i:https?)://")


class ResourceOut(ResourceIn, ORMModel):
    id: str
    skill_id: str
