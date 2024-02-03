import datetime
from typing import List

from pydantic import BaseModel, Field

from domain.user.user_schema import ResponseUserDetail


class UserDetail(ResponseUserDetail):
    id: int = Field(ge=1)
    is_banned: bool
    is_superuser: bool


class ResponseUserDetailList(BaseModel):
    users: List["UserDetail"]


class RequestUserBanUpdate(BaseModel):
    user_id: int = Field(ge=1)
    is_banned: bool


class RequestBoradCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    information: str = Field(min_length=1, max_length=512)
    is_visible: bool


class RequestUserBoardPermissionUpdate(BaseModel):
    user_id: int = Field(ge=1)
    board_id: int = Field(ge=1)
    is_permitted: bool
