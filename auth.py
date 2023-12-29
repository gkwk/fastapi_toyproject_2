from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import User
from database import get_data_base
from config import get_settings

ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().APP_JWT_EXPIRE_MINUTES
SECRET_KEY = get_settings().APP_JWT_SECRET_KEY
ALGORITHM = get_settings().PASSWORD_ALGORITHM
oauth2_scheme_user = OAuth2PasswordBearer(
    tokenUrl=get_settings().APP_JWT_USER_URL, scheme_name="user_oauth2_schema"
)
oauth2_scheme_admin = OAuth2PasswordBearer(
    tokenUrl=get_settings().APP_JWT_ADMIN_URL, scheme_name="admin_oauth2_schema"
)

password_context = CryptContext(schemes=["bcrypt"])


def get_oauth2_scheme_user():
    return oauth2_scheme_user


def get_oauth2_scheme_admin():
    return oauth2_scheme_admin


def get_password_context():
    return password_context


def generate_user_token(
    form_data: OAuth2PasswordRequestForm,
    data_base: Session,
):
    user = data_base.query(User).filter_by(name=form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="입력된 이름을 가지는 유저가 존재하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not get_password_context().verify(
        (form_data.password + user.password_salt), user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = {
        "sub": "user_token",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        get_settings().APP_DOMAIN: True,
        "user_name": user.name,
        "user_id": user.id,
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
    }


def check_and_decode_user_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="토큰이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("user_name")
        user_id: int = payload.get("user_id")

        if (user_name is None) or (user_id is None):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return payload


def generate_admin_token(
    form_data: OAuth2PasswordRequestForm,
    data_base: Session,
):
    admin = data_base.query(User).filter_by(name=form_data.username).first()

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="입력된 이름을 가지는 관리자가 존재하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not get_password_context().verify(
        (form_data.password + admin.password_salt), admin.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="패스워드가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 권한이 존재하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = {
        "sub": "admin_token",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        get_settings().APP_DOMAIN: True,
        "admin_name": admin.name,
        "admin_id": admin.id,
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": admin.name,
        "is_admin": True,
    }


def check_and_decode_admin_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="토큰이 유효하지 않습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_name: str = payload.get("admin_name")
        admin_id: int = payload.get("admin_id")
        if (admin_name is None) or (admin_id is None):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return payload
