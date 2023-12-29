from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import get_data_base
from domain.admin import admin_schema, admin_crud
from domain.user.user_crud import get_oauth2_scheme

router = APIRouter(
    prefix="/api/admin",
)


@router.get("/users", response_model=admin_schema.UserMoreDetailList)
def get_users(
    token=Depends(get_oauth2_scheme(is_admin=True)),
    data_base: Session = Depends(get_data_base),
):
    data = admin_crud.check_and_decode_admin_token(token=token, data_base=data_base)
    users = admin_crud.get_users(data_base=data_base)

    return {"users": users}


@router.post("/login", response_model=admin_schema.AdminToken)
def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    data_base: Session = Depends(get_data_base),
):
    return admin_crud.generate_admin_token(form_data=form_data, data_base=data_base)


@router.post("/update_user_is_banned", status_code=status.HTTP_204_NO_CONTENT)
def update_user_is_banned(
    schema: admin_schema.UserBanOption,
    token=Depends(get_oauth2_scheme(is_admin=True)),
    data_base: Session = Depends(get_data_base),
):
    data = admin_crud.check_and_decode_admin_token(token=token, data_base=data_base)

    return admin_crud.update_user_is_banned(data_base=data_base, schema=schema)
