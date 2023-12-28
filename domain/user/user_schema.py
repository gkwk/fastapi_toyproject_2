import datetime

from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo


class UserCreate(BaseModel):
    name: str
    password1: str
    password2: str
    email: EmailStr

    @field_validator("name", "password1", "password2", "email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value

    @field_validator("password2")
    def password_confirm(cls, value, info: FieldValidationInfo):
        if "password1" in info.data and value != info.data["password1"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return value


class UserReadWithEmailAndName(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name", "email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class UserUpdate(BaseModel):
    email: EmailStr

    @field_validator("email")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value


class UserUpdatePassword(BaseModel):
    password1: str
    password2: str

    @field_validator("password1", "password2")
    def is_not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("값이 공백일 수 없습니다.")
        return value

    @field_validator("password2")
    def password_confirm(cls, value, info: FieldValidationInfo):
        if "password1" in info.data and value != info.data["password1"]:
            raise ValueError("비밀번호가 일치하지 않습니다")
        return value


class UserToken(BaseModel):
    access_token: str
    token_type: str
    user_name: str


class UserDetail(BaseModel):
    name: str
    email: EmailStr
    join_date: datetime.datetime
