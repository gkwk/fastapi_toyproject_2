import datetime
from typing import List

from pydantic import BaseModel, field_validator, EmailStr, Field
from pydantic_core.core_schema import ValidationInfo


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    password1: str = Field(min_length=8, max_length=32)
    password2: str = Field(min_length=8, max_length=32)
    email: EmailStr = Field(min_length=1, max_length=256)

    @field_validator("name", "password1", "password2", "email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value

    @field_validator("password2")
    def password_confirm(cls, value, info: ValidationInfo):
        if "password1" in info.data and value != info.data["password1"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return value


class UserReadWithEmailAndName(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    email: EmailStr = Field(min_length=1, max_length=256)

    @field_validator("name", "email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class UserUpdate(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=256)

    @field_validator("email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class UserUpdatePassword(BaseModel):
    password1: str = Field(min_length=8, max_length=32)
    password2: str = Field(min_length=8, max_length=32)

    @field_validator("password1", "password2")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value

    @field_validator("password2")
    def password_confirm(cls, value, info: ValidationInfo):
        if "password1" in info.data and value != info.data["password1"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return value


class UserToken(BaseModel):
    access_token: str
    token_type: str


class BoardID(BaseModel):
    id: int = Field(ge=1)


class PostID(BaseModel):
    name: str
    board_id: int = Field(ge=1)
    id: int = Field(ge=1)


class UserDetail(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    email: EmailStr = Field(min_length=1, max_length=256)
    join_date: datetime.datetime
    boards: List["BoardID"]
    posts: List["PostID"]
