from pydantic import BaseModel, Field

from app.core.base_schema import UTCDateTime


class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=256)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: UTCDateTime


class MeOut(BaseModel):
    username: str
