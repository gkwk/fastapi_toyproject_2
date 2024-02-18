from datetime import datetime
import secrets
import getpass

from starlette import status

from sqlalchemy.orm import Session

from models import User, Board, UserPermissionTable, JWTRefreshTokenList
from domain.user.user_crud import (
    get_user_with_username,
    get_user_with_email,
)
from domain.user.user_schema import RequestUserCreate
from database import data_base_dependency, get_data_base_decorator
from auth import get_password_context, ban_access_token,current_user_payload,current_admin_payload
from http_execption_params import http_exception_params


@get_data_base_decorator
def create_admin_with_terminal(data_base: Session = None):
    generated_password_salt = secrets.token_hex(4)

    while True:
        try:
            name = input("Admin name : ")
            if get_user_with_username(data_base=data_base, name=name):
                raise ValueError(
                    http_exception_params["already_user_name_existed"]["detail"]
                )
            break
        except Exception as ex:
            print(ex)

    while True:
        try:
            email = input("Admin email : ")
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
            password1 = getpass.getpass("Password : ")
            password2 = getpass.getpass("Password Confirm : ")
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
    user_id_list: list[int] = None,
):
    board = Board(name=name, information=information, is_visible=is_visible)
    data_base.add(board)
    data_base.commit()

    users = []
    board.permission_verified_user_id_range = (
        data_base.query(User).order_by(User.id.desc()).first().id
    )

    if board.is_visible:
        if not user_id_list:
            users = data_base.query(User).order_by(User.id.asc()).all()
        else:
            users = (
                data_base.query(User)
                .filter(User.id.in_(user_id_list))
                .order_by(User.id.asc())
                .all()
            )
    else:
        if not user_id_list:
            users = (
                data_base.query(User)
                .filter_by(is_superuser=True)
                .order_by(User.id.asc())
                .all()
            )
        else:
            users = (
                data_base.query(User)
                .filter(User.id.in_(user_id_list))
                .order_by(User.id.asc())
                .all()
            )

    if users:
        for user in users:
            user.boards.append(board)

    data_base.commit()

    users_refresh_token_table = (
        data_base.query(JWTRefreshTokenList)
        .filter(JWTRefreshTokenList.user_id <= board.permission_verified_user_id_range)
        .all()
    )

    for user in users_refresh_token_table:
        ban_access_token(
            data_base=data_base,
            user_id=user.user_id,
            user_access_token=user.access_token,
        )


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


def get_board(
    data_base: data_base_dependency,
    board_id: int,
):
    return data_base.query(Board).filter_by(id=board_id).first()


def get_boards(
    data_base: data_base_dependency,
    token: current_user_payload,
    is_visible: bool | None,
    is_available: bool | None,
    skip: int | None,
    limit: int | None,
):

    filter_kwargs = {}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    if token.get("is_admin"):
        if is_visible != None:
            filter_kwargs["is_visible"] = is_visible
        if is_available != None:
            filter_kwargs["is_available"] = is_available
    else:
        filter_kwargs["is_visible"] = True
        filter_kwargs["is_available"] = True

    boards = data_base.query(Board).filter_by(**filter_kwargs).order_by(Board.id.asc())
    total = boards.count()
    boards = boards.offset(skip).limit(limit).all()
    return {"total": total, "boards": boards}


def update_board(
    data_base: data_base_dependency,
    token: current_admin_payload,
    id: int,
    name : str | None,
    information : str| None,
    is_visible: bool| None,
    is_available:bool| None,
):
    board = data_base.query(Board).filter_by(id=id).first()

    # if not ai:
    #     raise HTTPException(**http_exception_params["ai_model_not_found"])

    if name != None:
        board.name = name
    if information != None:
        board.information = information
    if is_visible != None:
        board.is_visible = is_visible
    if is_available != None:
        board.is_available = is_available

    data_base.add(board)
    data_base.commit()


def delete_board(
    data_base: data_base_dependency,
    token: current_admin_payload,
    id: int,
):
    board = data_base.query(Board).filter_by(id=id).first()

    # if not board:
    #     raise HTTPException(**http_exception_params["ai_model_not_found"])


    data_base.delete(board)
    data_base.commit()
