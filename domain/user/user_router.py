from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import get_data_base
from domain.user import user_schema, user_crud
from auth import (
    get_oauth2_scheme_user,
    check_and_decode_user_token,
    generate_user_token,
)


router = APIRouter(
    prefix="/api/user",
)


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def create_user(
    schema: user_schema.UserCreate, data_base: Session = Depends(get_data_base)
):
    user_crud.create_user(data_base=data_base, schema=schema)


@router.post("/login", response_model=user_schema.UserToken)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    data_base: Session = Depends(get_data_base),
):
    return generate_user_token(form_data=form_data, data_base=data_base)


@router.get("/detail", response_model=user_schema.UserDetail)
def get_user_detail(
    token=Depends(get_oauth2_scheme_user()), data_base: Session = Depends(get_data_base)
):
    data = check_and_decode_user_token(token=token)

    return user_crud.get_user_with_id_and_name(
        data_base=data_base, user_name=data["user_name"], user_id=data["user_id"]
    )


@router.put("/update_detail", status_code=status.HTTP_204_NO_CONTENT)
def update_user_detail(
    schema: user_schema.UserUpdate,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    user_crud.update_user(data_base=data_base, schema=schema, decoded_token=data)


@router.put("/update_password", status_code=status.HTTP_204_NO_CONTENT)
def update_user_detail(
    schema: user_schema.UserUpdatePassword,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    user_crud.update_user_password(
        data_base=data_base, schema=schema, decoded_token=data
    )
