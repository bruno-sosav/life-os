from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class BusinessIdeaIn(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str | None = None
    tags: list[str] | None = None


class BusinessIdeaOut(BusinessIdeaIn, ORMModel):
    id: str
    created_at: UTCDateTime
