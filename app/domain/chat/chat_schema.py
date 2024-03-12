import datetime
from typing import List

from pydantic import BaseModel, field_validator, Field


class RequestChatSessionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    information: str = Field(min_length=1, max_length=256)
    is_visible: bool
    is_closed: bool

    @field_validator("name", "information")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestChatSessionRead(BaseModel):
    chatting_room_id: int = Field(ge=1)


class RequestChatSessionsRead(BaseModel):
    user_create_id: int | None = Field(default=None,ge=1)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=0)


class RequestChatSessionUpdate(BaseModel):
    id: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=64)
    information: str | None = Field(default=None, min_length=1, max_length=256)
    is_visible: bool | None = Field(default=None)
    is_closed: bool | None = Field(default=None)

    @field_validator("name", "information")
    def is_not_empty(cls, value: str):
        if value != None:
            if not value.strip():
                raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestChatSessionDelete(BaseModel):
    id: int = Field(ge=1)


class RequestChatCreate(BaseModel):
    content: str = Field(max_length=256)
    chat_session_id: int = Field(ge=1)

    @field_validator("content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestChatsRead(BaseModel):
    chat_session_id: int = Field(ge=1)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=0)


class RequestChatUpdate(BaseModel):
    id: int = Field(ge=1)
    chat_session_id: int = Field(ge=1)
    content: str | None = Field(default=None, max_length=256)
    is_visible: bool | None = Field(default=None)


class RequestChatDelete(BaseModel):
    id: int = Field(ge=1)
    chat_session_id: int = Field(ge=1)
