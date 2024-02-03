import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, Field


class RequestAICreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=256)
    is_visible: bool = Field(default=True)

    @field_validator("name", "description")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestAIRead(BaseModel):
    ai_id: int = Field(ge=1)


class RequestAIsRead(BaseModel):
    is_visible: bool | None = Field(default=None)
    is_available: bool | None = Field(default=None)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1)


class RequestAIUpdate(BaseModel):
    ai_id: int = Field(ge=1)
    description: str | None = Field(default=None, max_length=256)
    is_visible: bool | None = Field(default=None)
    is_available: bool | None = Field(default=None)


class RequestAIDelete(BaseModel):
    ai_id: int = Field(ge=1)


class RequestAILogCreate(BaseModel):
    ai_id: int = Field(ge=1)
    description: str = Field(min_length=1, max_length=256)

    @field_validator("description")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestAILogRead(BaseModel):
    ailog_id: int = Field(ge=1)


class RequestAILogsRead(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    ai_id: int | None = Field(default=None, ge=1)
    skip: int | None = Field(default=None, ge=0)
    limit: int | None = Field(default=None, ge=1)


class RequestAILogUpdate(BaseModel):
    ailog_id: int = Field(ge=1)
    description: str | None = Field(default=None, max_length=256)


class RequestAILogDelete(BaseModel):
    ailog_id: int = Field(ge=1)
