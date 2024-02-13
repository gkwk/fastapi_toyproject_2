from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from database import data_base_dependency
from domain.admin import admin_schema, admin_crud
from auth import (
    current_admin_payload,
    current_user_payload,
    validate_and_decode_admin_access_token,
    scope_checker
)
import v1_urn

router = APIRouter(prefix=v1_urn.ADMIN_PREFIX, tags=["admin"])


@router.get(
    v1_urn.ADMIN_GET_USERS,
    response_model=admin_schema.ResponseUserDetailList,
    dependencies=[Depends(validate_and_decode_admin_access_token)],
)
def get_users(
    # token: current_admin_payload,
    data_base: data_base_dependency,
):
    users = admin_crud.get_users(data_base=data_base)

    return {"users": users}


@router.put(
    v1_urn.ADMIN_UPDATE_USER_BOARD_PERMISSION, status_code=status.HTTP_204_NO_CONTENT
)
def update_user_board_permission(
    data_base: data_base_dependency,
    token: current_admin_payload,
    schema: admin_schema.RequestUserBoardPermissionUpdate,
):
    admin_crud.update_user_board_permission(
        data_base=data_base,
        user_id=schema.user_id,
        board_id=schema.board_id,
        is_visible=schema.is_permitted,
    )


@router.put(v1_urn.ADMIN_UPDATE_USER_IS_BANNED, status_code=status.HTTP_204_NO_CONTENT)
def update_user_is_banned(
    data_base: data_base_dependency,
    token: current_admin_payload,
    schema: admin_schema.RequestUserBanUpdate,
):
    admin_crud.update_user_is_banned(
        data_base=data_base,
        id=schema.user_id,
        is_banned=schema.is_banned,
    )


@router.post(v1_urn.ADMIN_CREATE_BOARD, status_code=status.HTTP_201_CREATED)
def create_board(
    data_base: data_base_dependency,
    token: current_admin_payload,
    schema: admin_schema.RequestBoradCreate,
):
    admin_crud.create_board(
        data_base=data_base,
        name=schema.name,
        information=schema.information,
        is_visible=schema.is_visible,
        user_id_list=schema.user_id_list,
    )

    return {"result": "success"}


@router.get(v1_urn.ADMIN_GET_BOARD)
def get_board(
    data_base: data_base_dependency,
    token: current_user_payload,
    # schema: Annotated[ai_schema.RequestAIRead, Depends()],
    board_id: int,
):
    scope_checker(token=token,target_scopes=[board_id])
    
    return admin_crud.get_board(
        data_base=data_base,
        board_id=board_id,
    )


@router.get(v1_urn.ADMIN_GET_BOARDS)
def get_boards(
    data_base: data_base_dependency,
    token: current_user_payload,
    # schema: Annotated[ai_schema.RequestAIsRead, Depends()],
    is_visible: bool | None = None,
    is_available: bool | None = None,
    skip: int | None = None,
    limit: int | None = None,
):
    return admin_crud.get_boards(
        data_base=data_base,
        token=token,
        is_visible=is_visible,
        is_available=is_available,
        skip=skip,
        limit=limit,
    )


@router.put(v1_urn.ADMIN_UPDATE_BOARD, status_code=status.HTTP_204_NO_CONTENT)
def update_board(
    data_base: data_base_dependency,
    token: current_admin_payload,
    # schema: ai_schema.RequestAIUpdate,
    id: int,
    name: str | None = None,
    information: str | None = None,
    is_visible: bool | None = None,
    is_available: bool | None = None,
):
    admin_crud.update_board(
        data_base=data_base,
        token=token,
        id=id,
        name=name,
        information=information,
        is_visible=is_visible,
        is_available=is_available,
    )


@router.delete(v1_urn.ADMIN_DELET_BOARD, status_code=status.HTTP_204_NO_CONTENT)
def delete_board(
    data_base: data_base_dependency,
    token: current_admin_payload,
    # schema: Annotated[ai_schema.RequestAIDelete, Depends()],
    board_id: int,
):
    admin_crud.delete_board(
        data_base=data_base,
        token=token,
        id=board_id,
    )
