from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagRead


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=50_000)


class NoteCreate(NoteBase):
    tag_names: list[str] = Field(default_factory=list, max_length=20)


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, max_length=50_000)
    tag_names: list[str] | None = Field(default=None, max_length=20)


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagRead] = []
