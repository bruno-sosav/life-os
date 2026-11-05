from typing import Literal

from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel

ResourceKind = Literal["curso", "link", "video", "otro"]


class ResourceIn(BaseModel):
    kind: ResourceKind = "link"
    name: str = Field(min_length=1, max_length=255)
    url: str | None = Field(default=None, max_length=500)


class ResourceOut(ResourceIn, ORMModel):
    id: str
    skill_id: str
