from datetime import timedelta, datetime
import secrets

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status
from jose import jwt, JWTError
from passlib.context import CryptContext

from models import User
from domain.user.user_schema import UserCreate
from database import get_data_base
from config import get_settings

ACCESS_TOKEN_EXPIRE_MINUTES = get_settings().APP_JWT_EXPIRE_MINUTES
SECRET_KEY = get_settings().APP_JWT_SECRET_KEY
ALGORITHM = get_settings().PASSWORD_ALGORITHM
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=get_settings().APP_JWT_URL)
password_context = CryptContext(schemes=["bcrypt"])


def does_user_already_exist(data_base: Session, user_create: UserCreate):
    return (
        data_base.query(User)
        .filter((User.name == user_create.name) | (User.email == user_create.email))
        .first()
    )


def create_user(data_base: Session, user_create: UserCreate):
    generated_password_salt = secrets.token_hex(4)
    user = User(
        name=user_create.name,
        password=get_password_context().hash(
            user_create.password1 + generated_password_salt
        ),
        password_salt=generated_password_salt,
        join_date=datetime.now(),
        email=user_create.email,
    )
    data_base.add(user)
    data_base.commit()


def get_user(data_base: Session, user_name: str):
    user = data_base.query(User).filter(User.name == user_name).first()
    return user


def get_user_detail(data_base: Session, user_id, user_name):
    user_detail = data_base.query(User).filter_by(id=user_id, name=user_name).first()
    return user_detail


def get_oauth2_scheme():
    return oauth2_scheme


def get_password_context():
    return password_context


def generate_user_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    data_base: Session = Depends(get_data_base),
):
    user = get_user(data_base=data_base, user_name=form_data.username)

    if (not user) or (
        not get_password_context().verify((form_data.password + user.password_salt), user.password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유저 이름 혹은 패스워드가 일치하지 않습니다.",
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
        user_detail = get_user_detail(data_base, user_name=user_name, user_id=user_id)
        if user_detail is None:
            raise credentials_exception

    return payload
