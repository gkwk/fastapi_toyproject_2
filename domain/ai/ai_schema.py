import datetime
from typing import List

from pydantic import BaseModel, field_validator


class AICreate(BaseModel):
    information: str
    is_visible: bool

    @field_validator("information")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class AIRead(BaseModel):
    ai_id: int


class AIsRead(BaseModel):
    skip: int
    limit: int


class AIUpdate(BaseModel):
    ai_id: int
    information: str | None
    is_visible: bool | None


class AIDelete(BaseModel):
    ai_id: int


class AILogCreate(BaseModel):
    ai_id: int
    information: str

    @field_validator("information")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class AILogRead(BaseModel):
    ailog_id: int


class AILogsRead(BaseModel):
    skip: int | None
    limit: int | None


class AILogUpdate(BaseModel):
    ailog_id: int
    information: str | None


class AILogDelete(BaseModel):
    ailog_id: int
