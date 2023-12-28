from datetime import timedelta, datetime
import secrets
import getpass

from sqlalchemy.orm import Session
from models import User
from domain.user.user_crud import (
    does_user_name_already_exist,
    does_user_email_already_exist,
    get_password_context,
)
from domain.user.user_schema import UserCreate
from database import session_local


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
