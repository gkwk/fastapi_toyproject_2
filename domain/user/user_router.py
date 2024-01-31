from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from database import data_base_dependency
from domain.user import user_schema, user_crud
from auth import (
    generate_access_token,
    current_user_payload,
)


router = APIRouter(
    prefix="/user",
)


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def create_user(schema: user_schema.UserCreate, data_base: data_base_dependency):
    user_crud.create_user(data_base=data_base, schema=schema)


@router.post("/login", response_model=user_schema.UserToken)
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    data_base: data_base_dependency,
):
    return generate_access_token(form_data=form_data, data_base=data_base)


@router.get("/detail", response_model=user_schema.UserDetail)
def get_user_detail(token: current_user_payload, data_base: data_base_dependency):
    return user_crud.get_user_with_id_and_name(
        data_base=data_base, user_name=token["user_name"], user_id=token["user_id"]
    )


@router.put("/update_detail", status_code=status.HTTP_204_NO_CONTENT)
def update_user_detail(
    schema: user_schema.UserUpdate,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    user_crud.update_user(data_base=data_base, schema=schema, decoded_token=token)


@router.put("/update_password", status_code=status.HTTP_204_NO_CONTENT)
def update_user_password(
    schema: user_schema.UserUpdatePassword,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    user_crud.update_user_password(
        data_base=data_base, schema=schema, decoded_token=token
    )
