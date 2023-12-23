from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import get_data_base
from domain.user import user_schema, user_crud
from domain.user.user_crud import (
    generate_user_token,
    check_and_decode_user_token,
    get_oauth2_scheme,
)

router = APIRouter(
    prefix="/api/user",
)


@router.get("/detail", response_model=user_schema.UserReadDetail)
def get_user_detail(
    token=Depends(get_oauth2_scheme()), data_base: Session = Depends(get_data_base)
):
    data = check_and_decode_user_token(token=token, data_base=data_base)

    return user_crud.get_user_detail(
        data_base=data_base, user_name=data["user_name"], user_id=data["user_id"]
    )


@router.post("/register", status_code=status.HTTP_204_NO_CONTENT)
def register_user(
    user_create: user_schema.UserCreate, data_base: Session = Depends(get_data_base)
):
    if user_crud.does_user_already_exist(data_base=data_base, user_create=user_create):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 이름 혹은 이메일을 사용중인 사용자가 이미 존재합니다.",
        )
    user_crud.create_user(data_base=data_base, user_create=user_create)


@router.post("/login", response_model=user_schema.UserToken)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    data_base: Session = Depends(get_data_base),
):
    return generate_user_token(form_data=form_data, data_base=data_base)
