from datetime import datetime
import secrets

from fastapi import HTTPException
from starlette import status

from models import User
from domain.user.user_schema import (
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
)
from auth import get_password_context, token_dependency
from database import data_base_dependency

http_exception_params = {
    "already_user_name_existed": {
        "status_code": status.HTTP_409_CONFLICT,
        "detail": "동일한 이름을 사용중인 유저가 이미 존재합니다.",
    },
    "already_user_email_existed": {
        "status_code": status.HTTP_409_CONFLICT,
        "detail": "동일한 이메일을 사용중인 유저가 이미 존재합니다.",
    },
    "user_not_existed": {
        "status_code": status.HTTP_404_NOT_FOUND,
        "detail": "유저가 존재하지 않습니다.",
    },
}


def get_user_with_username(data_base: data_base_dependency, user_name: str):
    return data_base.query(User).filter_by(name=user_name).first()


def get_user_with_email(data_base: data_base_dependency, user_email: str):
    return data_base.query(User).filter_by(email=user_email).first()


def get_user_with_username_and_email(
    data_base: data_base_dependency, user_name: str, user_email: str
):
    return (
        data_base.query(User)
        .filter((User.name == user_name) | (User.email == user_email))
        .first()
    )


def get_user_with_id_and_name(
    data_base: data_base_dependency, user_id: int, user_name: str
):
    return data_base.query(User).filter_by(id=user_id, name=user_name).first()


def create_user(data_base: data_base_dependency, schema: UserCreate):
    if get_user_with_username(data_base=data_base, user_name=schema.name):
        raise HTTPException(**http_exception_params["already_user_name_existed"])
    if get_user_with_email(data_base=data_base, user_email=schema.email):
        raise HTTPException(**http_exception_params["already_user_email_existed"])

    generated_password_salt = secrets.token_hex(4)
    user = User(
        name=schema.name,
        password=get_password_context().hash(
            schema.password1 + generated_password_salt
        ),
        password_salt=generated_password_salt,
        join_date=datetime.now(),
        email=schema.email,
    )
    data_base.add(user)
    data_base.commit()


def update_user(
    data_base: data_base_dependency, schema: UserUpdate, decoded_token: token_dependency
):
    user = get_user_with_id_and_name(
        data_base=data_base,
        user_name=decoded_token["user_name"],
        user_id=decoded_token["user_id"],
    )
    if not user:
        raise HTTPException(**http_exception_params["user_not_existed"])
    if get_user_with_email(data_base=data_base, user_email=schema.email):
        raise HTTPException(**http_exception_params["already_user_email_existed"])

    user.email = schema.email
    data_base.add(user)
    data_base.commit()


def update_user_password(
    data_base: data_base_dependency,
    schema: UserUpdatePassword,
    decoded_token: token_dependency,
):
    user = get_user_with_id_and_name(
        data_base=data_base,
        user_name=decoded_token["user_name"],
        user_id=decoded_token["user_id"],
    )
    if not user:
        raise HTTPException(**http_exception_params["user_not_existed"])

    generated_password_salt = secrets.token_hex(4)
    user.password = get_password_context().hash(
        schema.password1 + generated_password_salt
    )
    user.password_salt = generated_password_salt
    data_base.add(user)
    data_base.commit()
