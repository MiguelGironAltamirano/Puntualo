from datetime import datetime

from pydantic import BaseModel, Field


class SessionOut(BaseModel):
    session_id: str


class MessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
