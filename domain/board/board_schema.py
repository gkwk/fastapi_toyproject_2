import datetime
from typing import List

from pydantic import BaseModel, field_validator


class PostCreate(BaseModel):
    name: str
    content: str
    board_id: int
    is_file_attached: bool
    is_visible: bool

    @field_validator("name", "content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class PostRead(BaseModel):
    id: int
    name: str
    content: str
    board_id: int
    create_date: datetime.datetime
    update_date: datetime.datetime | None
    number_of_view: int
    number_of_comment: int
    number_of_like: int
    is_file_attached: bool
    is_visible: bool


class PostsRead(BaseModel):
    total: int
    posts: List["PostRead"]


class PostUpdate(PostCreate):
    id: int


class PostDelete(BaseModel):
    id: int
    board_id: int
