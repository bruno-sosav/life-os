from pydantic import BaseModel


class StreakOut(BaseModel):
    streak: int
