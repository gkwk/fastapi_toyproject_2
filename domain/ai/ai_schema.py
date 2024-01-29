import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, Field


class AICreate(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    is_visible: bool = Field(default=True)

    @field_validator("name", "description")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class AIRead(BaseModel):
    ai_id: int = Field(ge=1)


class AIsRead(BaseModel):
    is_visible: bool | None = Field(default=None)
    is_available: bool | None = Field(default=None)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1)


class AIUpdate(BaseModel):
    ai_id: int = Field(ge=1)
    description: str | None = Field(default=None)
    is_visible: bool | None = Field(default=None)
    is_available: bool | None = Field(default=None)


class AIDelete(BaseModel):
    ai_id: int = Field(ge=1)


class AILogCreate(BaseModel):
    ai_id: int = Field(ge=1)
    description: str = Field(min_length=1)

    @field_validator("description")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class AILogRead(BaseModel):
    ailog_id: int = Field(ge=1)


class AILogsRead(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    ai_id: int | None = Field(default=None, ge=1)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1)


class AILogUpdate(BaseModel):
    ailog_id: int = Field(ge=1)
    description: str | None = Field(default=None)


class AILogDelete(BaseModel):
    ailog_id: int = Field(ge=1)
