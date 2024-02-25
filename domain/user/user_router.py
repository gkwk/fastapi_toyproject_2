from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from database import data_base_dependency
from domain.user import user_schema, user_crud
from auth import (
    current_user_payload,
    current_refresh_token_payload,
    generate_user_tokens,
    refresh_access_token,
    delete_refresh_token,
)
import v1_urn

router = APIRouter(prefix=v1_urn.USER_PREFIX, tags=["user"])


@router.post(v1_urn.USER_CREATE_USER, status_code=status.HTTP_201_CREATED)
def create_user(
    data_base: data_base_dependency,
    schema: user_schema.RequestUserCreate,
):
    user_id = user_crud.create_user(
        data_base=data_base,
        name=schema.name,
        password=schema.password1,
        email=schema.email,
    )

    return {"result": "success", "id" : user_id}


@router.post(v1_urn.USER_LOGIN_USER, response_model=user_schema.ResponseUserToken)
def login_user(
    data_base: data_base_dependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return generate_user_tokens(form_data=form_data, data_base=data_base)


@router.post(v1_urn.USER_REFRESH_USER, response_model=user_schema.ResponseAccessToken)
def refresh_user(
    data_base: data_base_dependency,
    refresh_token: current_refresh_token_payload,
):
    return refresh_access_token(
        data_base=data_base,
        refresh_token=refresh_token,
    )


@router.post(v1_urn.USER_LOGOUT_USER)
def logout_user(data_base: data_base_dependency, token: current_user_payload):
    delete_refresh_token(data_base=data_base, user_id=token.get("user_id"))

    return {"result": "success"}


@router.get(v1_urn.USER_GET_USER_DETAIL, response_model=user_schema.ResponseUserDetail)
def get_user_detail(
    data_base: data_base_dependency,
    token: current_user_payload,
):

    return user_crud.get_user_detail(
        data_base=data_base,
        name=token.get("user_name"),
        id=token.get("user_id"),
    )


@router.put(v1_urn.USER_UPDATE_USER_DETAIL, status_code=status.HTTP_204_NO_CONTENT)
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


@router.put(v1_urn.USER_UPDATE_USER_PASSWORD, status_code=status.HTTP_204_NO_CONTENT)
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


@router.put(v1_urn.USER_DELETE_USER, status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    token: current_user_payload,
    data_base: data_base_dependency,
):
    user_crud.delete_user(
        data_base=data_base,
        token=token,
    )
