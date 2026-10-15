from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["to-read", "reading", "finished"]


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=120)
    status: Status = "to-read"
    rating: Optional[int] = Field(default=None, ge=1, le=5)


class BookCreate(BookBase):
    pass


class BookUpdate(BookBase):
    pass


class BookOut(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
