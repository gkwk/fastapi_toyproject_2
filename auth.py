from datetime import timedelta, datetime
from typing import Annotated
import uuid

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import column
from starlette import status
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import User, JWTAccessTokenBlackList, JWTRefreshTokenList
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
        "status_code": status.HTTP_403_FORBIDDEN,
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
        "status_code": status.HTTP_403_FORBIDDEN,
        "detail": "차단되었습니다.",
        "headers": {"WWW-Authenticate": "Bearer"},
    },
}


def ban_access_token(
    data_base: data_base_dependency,
    user_id: int,
    user_access_token: str,
):
    user_old_access_token = (
        data_base.query(JWTAccessTokenBlackList)
        .filter_by(
            user_id=user_id,
            access_token=user_access_token,
        )
        .first()
    )

    if not user_old_access_token:
        user_old_access_token = JWTAccessTokenBlackList(
            user_id=user_id,
            access_token=user_access_token,
            expired_date=datetime.now() + timedelta(days=1),
        )

        data_base.add(user_old_access_token)
        data_base.commit()


def generate_refresh_token(
    data_base: data_base_dependency,
    user_id: int,
):
    data = {
        "sub": "refresh_token",
        "exp": datetime.utcnow() + timedelta(days=1),
        get_settings().APP_DOMAIN: True,
        "user_id": user_id,
        "uuid": str(uuid.uuid4()),
    }

    refresh_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    user_refresh_token = (
        data_base.query(JWTRefreshTokenList).filter_by(user_id=user_id).first()
    )

    if not user_refresh_token:
        user_refresh_token = JWTRefreshTokenList(
            user_id=user_id,
            refresh_token=refresh_token,
            expired_date=datetime.now() + timedelta(days=1),
        )
        data_base.add(user_refresh_token)
        data_base.commit()

    else:
        if user_refresh_token.access_token:
            ban_access_token(
                data_base=data_base,
                user_id=user_id,
                user_access_token=user_refresh_token.access_token,
            )

        user_refresh_token.refresh_token = refresh_token
        user_refresh_token.expired_date = datetime.now() + timedelta(days=1)
        data_base.add(user_refresh_token)
        data_base.commit()

    return refresh_token


def generate_access_token(
    data_base: data_base_dependency,
    user_id: int,
):
    user = data_base.query(User).filter_by(id=user_id).first()

    data = {
        "sub": "access_token",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        get_settings().APP_DOMAIN: True,
        "user_name": user.name,
        "user_id": user.id,
        "is_admin": user.is_superuser,
        "scope": [],
        "uuid": str(uuid.uuid4()),
    }

    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return access_token


def generate_user_tokens(
    form_data: OAuth2PasswordRequestForm,
    data_base: data_base_dependency,
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

    refresh_token = generate_refresh_token(data_base=data_base, user_id=user.id)
    access_token = generate_access_token(data_base=data_base, user_id=user.id)

    user_refresh_token = (
        data_base.query(JWTRefreshTokenList).filter_by(user_id=user.id).first()
    )
    user_refresh_token.access_token = access_token
    data_base.add(user_refresh_token)
    data_base.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def validate_and_decode_user_access_token(
    data_base: data_base_dependency, token: token_dependency
):
    credentials_exception = HTTPException(**http_exception_params["not_verified_token"])
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_name: str = payload.get("user_name")
        user_id: int = payload.get("user_id")

        access_token_blacklist = [
            values[0]
            for values in data_base.query(JWTAccessTokenBlackList)
            .filter_by(user_id=user_id)
            .with_entities(JWTAccessTokenBlackList.access_token)
        ]

        if (
            (user_name is None)
            or (user_id is None)
            or (token in access_token_blacklist)
        ):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return payload


def validate_and_decode_admin_access_token(
    data_base: data_base_dependency, token: token_dependency
):
    payload = validate_and_decode_user_access_token(data_base=data_base, token=token)
    if not payload.get("is_admin"):
        raise HTTPException(**http_exception_params["not_admin"])
    return payload


def validate_and_decode_refresh_token(
    data_base: data_base_dependency,
    request: Request,
):
    credentials_exception = HTTPException(**http_exception_params["not_verified_token"])
    try:
        token = (
            request.headers.get("Authorization")
            if request.headers.get("Authorization")
            else "None"
        )
        token = token.split()[-1]

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        user_refresh_token = (
            data_base.query(JWTRefreshTokenList)
            .filter_by(user_id=payload.get("user_id"))
            .first()
        )
        if (
            (user_id is None)
            or (user_refresh_token is None)
            or (user_refresh_token.refresh_token != token)
        ):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return payload


current_user_payload = Annotated[dict, Depends(validate_and_decode_user_access_token)]
current_admin_payload = Annotated[dict, Depends(validate_and_decode_admin_access_token)]
current_refresh_token_payload = Annotated[
    dict, Depends(validate_and_decode_refresh_token)
]


def refresh_access_token(
    data_base: data_base_dependency,
    refresh_token: current_refresh_token_payload,
):
    user_refresh_token = (
        data_base.query(JWTRefreshTokenList)
        .filter_by(user_id=refresh_token.get("user_id"))
        .first()
    )
    access_token = generate_access_token(
        data_base=data_base, user_id=user_refresh_token.user_id
    )
    ban_access_token(
        data_base=data_base,
        user_id=refresh_token.get("user_id"),
        user_access_token=user_refresh_token.access_token,
    )
    user_refresh_token.access_token = access_token
    data_base.add(user_refresh_token)
    data_base.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


def delete_refresh_token(
    data_base: data_base_dependency,
    user_id: int,
):
    user_refresh_token = (
        data_base.query(JWTRefreshTokenList).filter_by(user_id=user_id).first()
    )
    ban_access_token(
        data_base=data_base,
        user_id=user_id,
        user_access_token=user_refresh_token.access_token,
    )
    data_base.delete(user_refresh_token)
    data_base.commit()
