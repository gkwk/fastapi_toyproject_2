from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

from fastapi import Form, File, UploadFile

from pydantic import BaseModel, field_validator, Field


@dataclass
class RequestFormPostCreate:
    name: str = Form(min_length=1, max_length=64)
    content: str = Form(min_length=1, max_length=1024)
    board_id: int = Form(ge=1)
    is_file_attached: bool = Form(...)
    is_visible: bool = Form(...)
    files: list[Optional[UploadFile]] = File(None)


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
    user_id: int = Field(ge=1)
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


class RequestPostUpdate(BaseModel):
    id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=64)
    content: str | None = Field(default=None, min_length=1, max_length=1024)
    board_id: int = Field(ge=1)
    is_file_attached: bool | None = Field(default=None)
    is_visible: bool | None = Field(default=None)

    @field_validator("name", "content")
    def is_not_empty(cls, value: str):
        if (value != None) and (not value.strip()):
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestPostDelete(BaseModel):
    id: int = Field(ge=1)
    board_id: int = Field(ge=1)


@dataclass
class RequestFormCommentCreate:
    content: str = Form(min_length=1, max_length=256)
    post_id: int = Form(ge=1)
    is_file_attached: bool = Form(...)
    is_visible: bool = Form(...)
    files: list[Optional[UploadFile]] = File(None)


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


class RequestCommentUpdate(BaseModel):
    id: int = Field(ge=1)

    content: str | None = Field(default=None, min_length=1, max_length=256)
    post_id: int = Field(ge=1)
    is_file_attached: bool | None = Field(default=None)
    is_visible: bool | None = Field(default=None)

    @field_validator("content")
    def is_not_empty(cls, value: str):
        if (value != None) and (not value.strip()):
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class CommentDelete(BaseModel):
    id: int = Field(ge=1)
    post_id: int = Field(ge=1)


# class RequestPostCreateForm:
#     def __init__(
#         self,
#         *,
#         name: Annotated[str, Form(min_length=0, max_length=64)] = None,
#         content: Annotated[str, Form(min_length=0, max_length=1024)] = None,
#         board_id: Annotated[int, Form(ge=1)],
#         is_file_attached: Annotated[bool, Form()],
#         is_visible: Annotated[bool, Form()],
#         file: Optional[List[UploadFile]] = File(None),
#     ):
#         self.name = name
#         self.content = content
#         self.board_id = board_id
#         self.is_file_attached = is_file_attached
#         self.is_visible = is_visible
#         self.file = file
