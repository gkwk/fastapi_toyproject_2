import datetime
from typing import List

from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo

from domain.user.user_schema import UserDetail


class UserMoreDetail(UserDetail):
    id: int
    is_banned: bool
    is_superuser: bool


class UserMoreDetailList(BaseModel):
    users: List["UserMoreDetail"]


class AdminToken(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    is_admin: bool


class UserBanOption(BaseModel):
    id: int
    is_banned: bool

class BoradCreate(BaseModel):
    name: str
    information: str
    is_visible: bool