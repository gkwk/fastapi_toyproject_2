from datetime import datetime
import secrets
import getpass

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import User, Board, user_permisson_table
from domain.user.user_crud import (
    does_user_name_already_exist,
    does_user_email_already_exist,
)
from domain.user.user_schema import UserCreate
from domain.admin.admin_schema import (
    UserBanOption,
    BoradCreate,
    UserBoardPermissionSwitch,
)
from database import session_local
from auth import get_password_context


def get_users(data_base: Session):
    return data_base.query(User).all()


def update_user_is_banned(data_base: Session, schema: UserBanOption):
    user = data_base.query(User).filter_by(id=schema.id).first()
    user.is_banned = schema.is_banned
    data_base.add(user)
    data_base.commit()


def create_board(data_base: Session, schema: BoradCreate):
    board = Board(
        name=schema.name, information=schema.information, is_visible=schema.is_visible
    )
    data_base.add(board)
    data_base.commit()

    if board.is_visible:
        users = data_base.query(User).all()
        for user in users:
            user.boards.append(board)
    else:
        superusers = data_base.query(User).filter_by(is_superuser=True).all()
        for superuser in superusers:
            superuser.boards.append(board)

    data_base.commit()


def switch_user_board_permission(data_base: Session, schema: UserBoardPermissionSwitch):
    user = data_base.query(User).filter_by(id=schema.user_id).first()
    board = data_base.query(Board).filter_by(id=schema.board_id).first()
    query = user_permisson_table.select().where(
        user_permisson_table.c.user_id == schema.user_id,
        user_permisson_table.c.board_id == schema.board_id,
    )
    if schema.is_permitted:
        if not data_base.execute(query).fetchall():
            user.boards.append(board)
    else:
        if data_base.execute(query).fetchall():
            user.boards.remove(board)
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
