from pydantic import BaseModel, Field

from app.core.base_schema import Label, ORMModel, UTCDateTime

# Las etiquetas de ideas son libres: se ven tal cual, emoji incluido ("💬 Frase")
IdeaTag = Label

DEFAULT_TAG = "💡 Idea"


class IdeaIn(BaseModel):
    text: str = Field(min_length=1)
    author: str | None = Field(default=None, max_length=255)
    tag: IdeaTag = DEFAULT_TAG


class IdeaOut(IdeaIn, ORMModel):
    id: str
    created_at: UTCDateTime


class TagCount(BaseModel):
    tag: str
    count: int
