from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator, Field


class RequestPostCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    content: str = Field(min_length=1, max_length=1024)
    board_id: int = Field(ge=1)
    is_file_attached: bool
    is_visible: bool

    @field_validator("name", "content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestPostRead(BaseModel):
    id: int = Field(ge=1)
    board_id: int = Field(ge=1)


class RequestPostsRead(BaseModel):
    board_id: int = Field(ge=1)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1)


class ResponsePostRead(BaseModel):
    id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=64)
    content: str = Field(min_length=1, max_length=1024)
    board_id: int = Field(ge=1)
    create_date: datetime
    update_date: datetime | None
    number_of_view: int = Field(ge=0)
    number_of_comment: int = Field(ge=0)
    number_of_like: int = Field(ge=0)
    is_file_attached: bool
    is_visible: bool


class ResponsePostsRead(BaseModel):
    total: int = Field(ge=0)
    posts: List["ResponsePostRead"]


class RequestPostUpdate(RequestPostCreate):
    id: int = Field(ge=1)


class RequestPostDelete(BaseModel):
    id: int = Field(ge=1)
    board_id: int = Field(ge=1)


class RequestCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=256)
    post_id: int = Field(ge=1)
    is_file_attached: bool
    is_visible: bool

    @field_validator("content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestCommentRead(BaseModel):
    id: int = Field(ge=1)
    post_id: int = Field(ge=1)


class RequestCommentsRead(BaseModel):
    post_id: int = Field(ge=1)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1)


class ResponseCommentRead(BaseModel):
    id: int = Field(ge=1)
    content: str = Field(min_length=1, max_length=256)
    post_id: int = Field(ge=1)
    user_id: int = Field(ge=1)
    create_date: datetime
    update_date: datetime | None
    is_file_attached: bool
    is_visible: bool


class ResponseCommentsRead(BaseModel):
    total: int = Field(ge=0)
    comments: List["ResponseCommentRead"]


class RequestCommentUpdate(RequestCommentCreate):
    id: int = Field(ge=1)


class CommentDelete(BaseModel):
    id: int = Field(ge=1)
    post_id: int = Field(ge=1)
