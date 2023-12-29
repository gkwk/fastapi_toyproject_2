from datetime import timedelta, datetime
import secrets
import getpass

from sqlalchemy.orm import Session

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
from domain.admin.admin_schema import UserMoreDetailList

from database import get_data_base
from config import get_settings

from models import User
from domain.user.user_crud import (
    does_user_name_already_exist,
    does_user_email_already_exist,
    get_password_context,
    get_user_with_name,
    get_oauth2_scheme,
    get_user_with_id_and_name,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM,
)
from domain.user.user_schema import UserCreate
from domain.admin.admin_schema import UserBanOption
from database import session_local


def get_users(data_base: Session):
    return data_base.query(User).all()


def update_user_is_banned(data_base: Session, schema: UserBanOption):
    user = data_base.query(User).filter_by(id=schema.id).first()
    user.is_banned = schema.is_banned
    data_base.add(user)
    data_base.commit()


def create_admin():
    data_base: Session = session_local()

    generated_password_salt = secrets.token_hex(4)

    while True:
        try:
            name = input("Admin name : ")
            email = input("Admin email : ")
            password1 = getpass.getpass("Password : ")
            password2 = getpass.getpass("Password Confirm : ")
            schema = UserCreate(
                name=name, password1=password1, password2=password2, email=email
            )

            if does_user_name_already_exist(data_base=data_base, schema=schema):
                raise ValueError("동일한 이름을 사용중인 유저가 이미 존재합니다.")
            if does_user_email_already_exist(data_base=data_base, schema=schema):
                raise ValueError("동일한 이메일을 사용중인 유저가 이미 존재합니다.")
        except Exception as ex:
            print(ex)
            continue

        if schema:
            break

    user = User(
        name=schema.name,
        password=get_password_context().hash(
            schema.password1 + generated_password_salt
        ),
        password_salt=generated_password_salt,
        join_date=datetime.now(),
        email=schema.email,
        is_superuser=True,
    )
    data_base.add(user)
    data_base.commit()

    data_base.close()


def generate_admin_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    data_base: Session = Depends(get_data_base),
):
    admin = get_user_with_name(data_base=data_base, user_name=form_data.username)

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


def check_and_decode_admin_token(
    token=Depends(get_oauth2_scheme(is_admin=True)),
    data_base: Session = Depends(get_data_base),
):
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
    else:
        admin = get_user_with_id_and_name(
            data_base, user_name=admin_name, user_id=admin_id
        )
        if (admin is None) or (not admin.is_superuser):
            raise credentials_exception

    return payload


def ban_user(
    token=Depends(get_oauth2_scheme(is_admin=True)),
    data_base: Session = Depends(get_data_base),
):
    pass
