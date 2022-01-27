from pydantic.fields import Field 
from pydantic import BaseModel
from fastapi import Form
from datetime import datetime

class Comment(BaseModel):
    content: str
    target_id: str
    # reply_to: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool
    like: int


class ReplyComment(BaseModel):
    content: str
    comment_id: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    is_deleted: bool