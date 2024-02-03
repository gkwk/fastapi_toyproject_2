import datetime
from typing import List

from pydantic import BaseModel, field_validator, Field


class RequestChatSessionCreate(BaseModel):
    content: str = Field(min_length=1, max_length=256)
    is_visible: bool

    @field_validator("content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestChatSessionRead(BaseModel):
    chatting_room_id: int = Field(ge=1)


class RequestChatSessionsRead(BaseModel):
    user_id: int | None = Field(ge=1)
    skip: int = Field(ge=0)
    limit: int = Field(ge=0)


class RequestChatSessionUpdate(BaseModel):
    chatting_room_id: int = Field(ge=1)
    content: str | None = Field(max_length=256)
    is_visible: bool | None


class RequestChatSessionDelete(BaseModel):
    chatting_room_id: int = Field(ge=1)


class RequestChatCreate(BaseModel):
    chat_content: str = Field(max_length=256)
    chatting_room_id: int = Field(ge=1)

    @field_validator("chat_content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestChatsRead(BaseModel):
    chatting_room_id: int = Field(ge=1)
    skip: int | None = Field(ge=0)
    limit: int | None = Field(ge=0)


class RequestChatUpdate(BaseModel):
    chat_id: int = Field(ge=1)
    chatting_room_id: int = Field(ge=1)
    content: str | None = Field(max_length=256)
    is_visible: bool | None


class RequestChatDelete(BaseModel):
    chat_id: int = Field(ge=1)
    chatting_room_id: int = Field(ge=1)
