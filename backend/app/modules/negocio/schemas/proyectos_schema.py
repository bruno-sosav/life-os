from pydantic import BaseModel, Field

from app.core.base_schema import ORMModel, UTCDateTime


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    color: str | None = "#0A84FF"
    emoji: str | None = "📁"
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    color: str | None = None


class ProjectOut(ProjectIn, ORMModel):
    id: str
    created_at: UTCDateTime
