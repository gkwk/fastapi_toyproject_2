import datetime
from typing import List

from pydantic import BaseModel, field_validator


class ChatSessionCreate(BaseModel):
    content: str
    is_visible: bool

    @field_validator("content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class ChatSessionRead(BaseModel):
    chatting_room_id: int


class ChatSessionsRead(BaseModel):
    skip: int
    limit: int


class ChatSessionUpdate(BaseModel):
    chatting_room_id: int
    content: str | None
    is_visible: bool | None


class ChatSessionDelete(BaseModel):
    chatting_room_id: int


class ChatCreate(BaseModel):
    chat_content: str
    chatting_room_id: int

    @field_validator("chat_content")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class ChatsRead(BaseModel):
    chatting_room_id: int
    skip: int | None
    limit: int | None


class ChatUpdate(BaseModel):
    chat_id: int
    chatting_room_id: int
    content: str | None
    is_visible: bool | None


class ChatDelete(BaseModel):
    chat_id: int
    chatting_room_id: int
