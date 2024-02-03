import secrets

from fastapi import HTTPException

from models import User
from auth import get_password_context, current_user_payload
from database import data_base_dependency
from http_execption_params import http_exception_params


def get_user_with_username(
    data_base: data_base_dependency,
    name: str,
):
    return data_base.query(User).filter_by(name=name).first()


def get_user_with_email(
    data_base: data_base_dependency,
    eamil: str,
):
    return data_base.query(User).filter_by(email=eamil).first()


def get_user_with_username_and_email(
    data_base: data_base_dependency,
    name: str,
    email: str,
):
    return (
        data_base.query(User)
        .filter((User.name == name) | (User.email == email))
        .first()
    )


def get_user_with_id_and_name(
    data_base: data_base_dependency,
    id: int,
    name: str,
):
    return data_base.query(User).filter_by(id=id, name=name).first()


def create_user(
    data_base: data_base_dependency,
    name: str,
    password: str,
    email: str,
):
    if get_user_with_username(data_base=data_base, name=name):
        raise HTTPException(**http_exception_params["already_user_name_existed"])
    if get_user_with_email(data_base=data_base, eamil=email):
        raise HTTPException(**http_exception_params["already_user_email_existed"])

    generated_password_salt = secrets.token_hex(4)
    user = User(
        name=name,
        password=get_password_context().hash(password + generated_password_salt),
        password_salt=generated_password_salt,
        email=email,
    )
    data_base.add(user)
    data_base.commit()


def get_user_detail(
    data_base: data_base_dependency,
    id: int,
    name: str,
):
    return data_base.query(User).filter_by(id=id, name=name).first()


def update_user(
    data_base: data_base_dependency,
    token: current_user_payload,
    email: str,
):
    user = (
        data_base.query(User)
        .filter_by(id=token.get("user_id"), name=token.get("user_name"))
        .first()
    )

    if not user:
        raise HTTPException(**http_exception_params["user_not_existed"])
    if get_user_with_email(data_base=data_base, eamil=email):
        raise HTTPException(**http_exception_params["already_user_email_existed"])

    user.email = email

    data_base.add(user)
    data_base.commit()


def update_user_password(
    data_base: data_base_dependency,
    token: current_user_payload,
    password: str,
):
    user = (
        data_base.query(User)
        .filter_by(id=token.get("user_id"), name=token.get("user_name"))
        .first()
    )

    if not user:
        raise HTTPException(**http_exception_params["user_not_existed"])

    generated_password_salt = secrets.token_hex(4)
    user.password = get_password_context().hash(password + generated_password_salt)
    user.password_salt = generated_password_salt

    data_base.add(user)
    data_base.commit()
