from pydantic import BaseModel, ConfigDict, Field


class TagBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagRead(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
