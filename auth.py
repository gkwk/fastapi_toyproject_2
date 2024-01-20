from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import User
from database import data_base_dependency
from config import get_settings

ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().APP_JWT_EXPIRE_MINUTES
SECRET_KEY = get_settings().APP_JWT_SECRET_KEY
ALGORITHM = get_settings().PASSWORD_ALGORITHM
oauth2_scheme_v1 = OAuth2PasswordBearer(
    tokenUrl=get_settings().APP_JWT_USER_URL, scheme_name="v1_oauth2_schema"
)

password_context = CryptContext(schemes=["bcrypt"])


def get_oauth2_scheme_v1():
    return oauth2_scheme_v1


def get_password_context():
    return password_context


token_dependency = Annotated[str, Depends(get_oauth2_scheme_v1())]
http_exception_params = {
    "not_user": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "유저가 존재하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "not_admin": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "관리자 권한이 존재하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "not_verified_password": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "패스워드가 일치하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "not_verified_token": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "토큰이 유효하지 않습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
    "banned": {
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "detail": "차단되었습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
}


def generate_access_token(
    form_data: OAuth2PasswordRequestForm, data_base: data_base_dependency
):
    user = data_base.query(User).filter_by(name=form_data.username).first()

    if not user:
        raise HTTPException(**http_exception_params["not_user"])

    if user.is_banned:
        raise HTTPException(**http_exception_params["banned"])

    if not get_password_context().verify(
        (form_data.password + user.password_salt), user.password
    ):
        raise HTTPException(**http_exception_params["not_verified_password"])

    data = {
        "sub": "access_token",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        get_settings().APP_DOMAIN: True,
        "user_name": user.name,
        "user_id": user.id,
        "is_admin": user.is_superuser,
        "scope": [],
    }

    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "token_type": "bearer"}


def validate_and_decode_user_access_token(token: token_dependency):
    credentials_exception = HTTPException(**http_exception_params["not_verified_token"])
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("user_name")
        user_id: int = payload.get("user_id")

        if (user_name is None) or (user_id is None):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return payload


def validate_and_decode_admin_access_token(token: token_dependency):
    payload = validate_and_decode_user_access_token(token=token)
    if not payload.get("is_admin"):
        raise HTTPException(**http_exception_params["not_admin"])
    return payload


current_user_payload = Annotated[dict, Depends(validate_and_decode_user_access_token)]
current_admin_payload = Annotated[dict, Depends(validate_and_decode_admin_access_token)]
