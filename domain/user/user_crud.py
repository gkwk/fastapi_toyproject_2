from datetime import timedelta, datetime
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import User
from domain.user.user_schema import (
    UserCreate,
    UserReadWithEmailAndName,
    UserUpdate,
    UserUpdatePassword,
)
from database import get_data_base
from config import get_settings

ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().APP_JWT_EXPIRE_MINUTES
SECRET_KEY = get_settings().APP_JWT_SECRET_KEY
ALGORITHM = get_settings().PASSWORD_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=get_settings().APP_JWT_URL, scheme_name="user_oauth2_schema")
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="/api/admin/login", scheme_name="admin_oauth2_schema")

password_context = CryptContext(schemes=["bcrypt"])


def does_user_name_already_exist(data_base: Session, schema: UserCreate):
    return data_base.query(User).filter_by(name=schema.name).first()


def does_user_email_already_exist(data_base: Session, schema: UserCreate):
    return data_base.query(User).filter_by(email=schema.email).first()


def does_user_already_exist(data_base: Session, schema: UserCreate):
    return (
        data_base.query(User)
        .filter((User.name == schema.name) | (User.email == schema.email))
        .first()
    )


def get_user_with_name(data_base: Session, user_name: str):
    user = data_base.query(User).filter(User.name == user_name).first()
    return user


def get_user_with_email(data_base: Session, schema: UserReadWithEmailAndName):
    user = data_base.query(User).filter_by(name=schema.name, email=schema.email).first()
    return user


def get_user_with_id_and_name(data_base: Session, user_id: int, user_name: str):
    user = data_base.query(User).filter_by(id=user_id, name=user_name).first()
    return user


def get_oauth2_scheme(is_admin=False):
    if is_admin:
        return oauth2_scheme_admin
    return oauth2_scheme


def get_password_context():
    return password_context


def create_user(data_base: Session, schema: UserCreate):
    if does_user_name_already_exist(data_base=data_base, schema=schema):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 이름을 사용중인 유저가 이미 존재합니다.",
        )
    if does_user_email_already_exist(data_base=data_base, schema=schema):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="동일한 이메일을 사용중인 유저가 이미 존재합니다.",
        )

    generated_password_salt = secrets.token_hex(4)
    user = User(
        name=schema.name,
        password=get_password_context().hash(
            schema.password1 + generated_password_salt
        ),
        password_salt=generated_password_salt,
        join_date=datetime.now(),
        email=schema.email,
    )
    data_base.add(user)
    data_base.commit()


def update_user(data_base: Session, schema: UserUpdate, decoded_token: dict):
    user = get_user_with_id_and_name(
        data_base=data_base,
        user_name=decoded_token["user_name"],
        user_id=decoded_token["user_id"],
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저가 존재하지 않습니다.",
        )

    user.email = schema.email
    data_base.add(user)
    data_base.commit()


def update_user_password(
    data_base: Session, schema: UserUpdatePassword, decoded_token: dict
):
    user = get_user_with_id_and_name(
        data_base=data_base,
        user_name=decoded_token["user_name"],
        user_id=decoded_token["user_id"],
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저가 존재하지 않습니다.",
        )

    generated_password_salt = secrets.token_hex(4)
    user.password = get_password_context().hash(
        schema.password1 + generated_password_salt
    )
    user.password_salt = generated_password_salt
    data_base.add(user)
    data_base.commit()


def generate_user_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    data_base: Session = Depends(get_data_base),
):
    user = get_user_with_name(data_base=data_base, user_name=form_data.username)

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
        "user_name": user.name,
        "user_id": user.id,
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
    }


def check_and_decode_user_token(
    token=Depends(get_oauth2_scheme()), data_base: Session = Depends(get_data_base)
):
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
    else:
        user_detail = get_user_with_id_and_name(
            data_base, user_name=user_name, user_id=user_id
        )
        if user_detail is None:
            raise credentials_exception

    return payload
