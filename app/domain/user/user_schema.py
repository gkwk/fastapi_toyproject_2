import datetime
import re
from typing import List


from pydantic import BaseModel, field_validator, EmailStr, Field, SecretStr
from pydantic_core.core_schema import ValidationInfo

name_regex = "^[a-zA-Z][A-Za-z\d_]{0,63}$"

password_regex = (
    "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$@!%&*?])[A-Za-z\d#$@!%&*?]{8,32}$"
)


class RequestUserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64, pattern=name_regex)
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

    @field_validator("password1", "password2")
    def is_password_proper(cls, value: str):
        if not re.match(password_regex, value):
            raise ValueError(
                "소문자, 대문자, 숫자, 특수문자(#$@!%&*?) 들이 모두 최소 한번씩 사용되어야 합니다."
            )
        return value


class RequestUserUpdate(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=256)

    @field_validator("email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class RequestUserUpdatePassword(BaseModel):
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

    @field_validator("password1", "password2")
    def is_password_proper(cls, value: str):
        if not re.match(password_regex, value):
            raise ValueError(
                "소문자, 대문자, 숫자, 특수문자(#$@!%&*?) 들이 모두 최소 한번씩 사용되어야 합니다."
            )
        return value


class ResponseUserToken(BaseModel):
    access_token: str
    # refresh_token: str
    token_type: str


class ResponseAccessToken(BaseModel):
    access_token: str
    token_type: str


class UserDetailBoard(BaseModel):
    id: int = Field(ge=1)


class UserDetailPost(BaseModel):
    id: int = Field(ge=1)
    name: str
    board_id: int = Field(ge=1)


class ResponseUserDetail(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    email: EmailStr = Field(min_length=1, max_length=256)
    join_date: datetime.datetime
    boards: List["UserDetailBoard"]
    posts: List["UserDetailPost"]


class AdminCreateName(BaseModel):
    name: str = Field(min_length=1, max_length=64, pattern=name_regex)

    @field_validator("name")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class AdminCreateEmail(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=256)

    @field_validator("email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class AdminCreatePassword(BaseModel):
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

    @field_validator("password1", "password2")
    def is_password_proper(cls, value: str):
        if not re.match(password_regex, value):
            raise ValueError(
                "소문자, 대문자, 숫자, 특수문자(#$@!%&*?) 들이 모두 최소 한번씩 사용되어야 합니다."
            )
        return value
