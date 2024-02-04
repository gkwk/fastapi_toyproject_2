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


router = APIRouter(prefix="/user", tags=["user"])


@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def create_user(
    data_base: data_base_dependency,
    schema: user_schema.RequestUserCreate,
):
    user_crud.create_user(
        data_base=data_base,
        name=schema.name,
        password=schema.password1,
        email=schema.email,
    )

    return {"result": "success"}


@router.post("/login_user", response_model=user_schema.ResponseUserToken)
def login_user(
    data_base: data_base_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return generate_access_token(form_data=form_data, data_base=data_base)


@router.get("/get_user_detail", response_model=user_schema.ResponseUserDetail)
def get_user_detail(
    data_base: data_base_dependency,
    token: current_user_payload,
):
    return user_crud.get_user_detail(
        data_base=data_base,
        name=token.get("user_name"),
        id=token.get("user_id"),
    )


@router.put("/update_user_detail", status_code=status.HTTP_204_NO_CONTENT)
def update_user_detail(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema: user_schema.RequestUserUpdate,
):
    user_crud.update_user(
        data_base=data_base,
        token=token,
        email=schema.email,
    )


@router.put("/update_user_password", status_code=status.HTTP_204_NO_CONTENT)
def update_user_password(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema: user_schema.RequestUserUpdatePassword,
):
    user_crud.update_user_password(
        data_base=data_base,
        token=token,
        password=schema.password1,
    )
