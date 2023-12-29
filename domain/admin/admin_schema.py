import datetime
from typing import List

from pydantic import BaseModel, field_validator, EmailStr
from pydantic_core.core_schema import FieldValidationInfo

from domain.user.user_schema import UserDetail


class UserDetailList(BaseModel):
    users: List["UserDetail"]


class AdminToken(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    is_admin: bool