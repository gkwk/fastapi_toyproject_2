from datetime import datetime
import secrets

from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models import User
from domain.user.user_schema import (
    UserCreate,
    UserReadWithEmailAndName,
    UserUpdate,
    UserUpdatePassword,
)
from auth import get_password_context


def does_user_name_already_exist(data_base: Session, schema: UserCreate):
    return data_base.query(User).filter_by(name=schema.name).first()


def does_user_email_already_exist(data_base: Session, schema: UserCreate):
    return data_base.query(User).filter_by(email=schema.email).first()


def does_user_already_exist(data_base: Session, schema: UserCreate):
    return (
        data_base.query(User)
        .filter((User.name == schema.name) | (User.email == schema.email))
        .first()
    )


def get_user_with_name(data_base: Session, user_name: str):
    user = data_base.query(User).filter(User.name == user_name).first()
    return user


def get_user_with_email(data_base: Session, schema: UserReadWithEmailAndName):
    user = data_base.query(User).filter_by(name=schema.name, email=schema.email).first()
    return user


def get_user_with_id_and_name(data_base: Session, user_id: int, user_name: str):
    user = data_base.query(User).filter_by(id=user_id, name=user_name).first()
    return user


def create_user(data_base: Session, schema: UserCreate):
    if does_user_name_already_exist(data_base=data_base, schema=schema):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 이름을 사용중인 유저가 이미 존재합니다.",
        )
    if does_user_email_already_exist(data_base=data_base, schema=schema):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 이메일을 사용중인 유저가 이미 존재합니다.",
        )

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


def update_user(data_base: Session, schema: UserUpdate, decoded_token: dict):
    user = get_user_with_id_and_name(
        data_base=data_base,
        user_name=decoded_token["user_name"],
        user_id=decoded_token["user_id"],
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저가 존재하지 않습니다.",
        )

    user.email = schema.email
    data_base.add(user)
    data_base.commit()


def update_user_password(
    data_base: Session, schema: UserUpdatePassword, decoded_token: dict
):
    user = get_user_with_id_and_name(
        data_base=data_base,
        user_name=decoded_token["user_name"],
        user_id=decoded_token["user_id"],
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저가 존재하지 않습니다.",
        )

    generated_password_salt = secrets.token_hex(4)
    user.password = get_password_context().hash(
        schema.password1 + generated_password_salt
    )
    user.password_salt = generated_password_salt
    data_base.add(user)
    data_base.commit()
