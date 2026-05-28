from pydantic import BaseModel, ConfigDict
from typing import Optional


class NoteBase(BaseModel):
    title: str
    content: str


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteResponse(NoteBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)