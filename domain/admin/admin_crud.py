from datetime import datetime
import secrets
import getpass

from starlette import status

from sqlalchemy.orm import Session

from models import User, Board, UserPermissionTable
from domain.user.user_crud import (
    get_user_with_username,
    get_user_with_email,
)
from domain.user.user_schema import RequestUserCreate
from database import data_base_dependency, get_data_base_decorator
from auth import get_password_context
from http_execption_params import http_exception_params


def get_users(data_base: data_base_dependency):
    return data_base.query(User).all()


def update_user_is_banned(data_base: data_base_dependency, id: int, is_banned: bool):
    user = data_base.query(User).filter_by(id=id).first()
    user.is_banned = is_banned
    data_base.add(user)
    data_base.commit()


def create_board(
    data_base: data_base_dependency,
    name: str,
    information: str,
    is_visible: bool,
):
    board = Board(name=name, information=information, is_visible=is_visible)
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


def update_user_board_permission(
    data_base: data_base_dependency, user_id: int, board_id: int, is_visible: bool
):
    user = data_base.query(User).filter_by(id=user_id).first()
    board = data_base.query(Board).filter_by(id=board_id).first()
    permission = (
        data_base.query(UserPermissionTable)
        .filter_by(user_id=user_id, board_id=board_id)
        .first()
    )

    if is_visible:
        if not permission:
            user.boards.append(board)
    else:
        if permission:
            user.boards.remove(board)

    # user_permisson_table을 table로 사용시의 코드
    # query = user_permisson_table.select().where(
    #     user_permisson_table.c.user_id == user_id,
    #     user_permisson_table.c.board_id == board_id,
    # )
    # if is_visible:
    #     if not data_base.execute(query).fetchall():
    #         user.boards.append(board)
    # else:
    #     if data_base.execute(query).fetchall():
    #         user.boards.remove(board)

    data_base.commit()


@get_data_base_decorator
def create_admin_with_terminal(data_base: Session):
    generated_password_salt = secrets.token_hex(4)

    while True:
        try:
            print("Admin name : ", end="")
            name = input()
            if get_user_with_username(data_base=data_base, name=name):
                raise ValueError(
                    http_exception_params["already_user_name_existed"]["detail"]
                )
            break
        except Exception as ex:
            print(ex)

    while True:
        try:
            print("Admin email : ", end="")
            email = input()
            if get_user_with_email(data_base=data_base, eamil=email):
                raise ValueError(
                    http_exception_params["already_user_email_existed"]["detail"]
                )
            RequestUserCreate(
                name=name, password1="12345678", password2="12345678", email=email
            )
            break
        except Exception as ex:
            print(ex)

    while True:
        try:
            print("Password : ", end="")
            password1 = getpass.getpass()
            print("Password Confirm : ", end="")
            password2 = getpass.getpass()
            schema = RequestUserCreate(
                name=name, password1=password1, password2=password2, email=email
            )
            break
        except Exception as ex:
            print(ex)

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
