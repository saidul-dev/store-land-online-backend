from datetime import datetime
from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str


class CommentRead(BaseModel):
    id: int
    content: str
    post_id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True
