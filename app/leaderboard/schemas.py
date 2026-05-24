from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Literal


Scope = Literal["global", "friends"]


class LeaderboardRow(BaseModel):
    user_id: UUID
    username: str
    total_score: int
    entries_count: int
    rank: int

    model_config = ConfigDict(from_attributes=True)
