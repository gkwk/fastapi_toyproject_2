from fastapi import APIRouter, Depends
from starlette import status

from database import data_base_dependency
from domain.admin import admin_schema, admin_crud
from auth import current_admin_payload, validate_and_decode_admin_access_token

router = APIRouter(
    prefix="/api/admin",
)


@router.get(
    "/users",
    response_model=admin_schema.UserMoreDetailList,
    dependencies=[Depends(validate_and_decode_admin_access_token)],
)
def get_users(
    # token: current_admin_payload,
    data_base: data_base_dependency,
):
    users = admin_crud.get_users(data_base=data_base)

    return {"users": users}


@router.put("/update_user_board_permission", status_code=status.HTTP_204_NO_CONTENT)
def update_user_board_permission(
    schema: admin_schema.UserBoardPermissionSwitch,
    token: current_admin_payload,
    data_base: data_base_dependency,
):
    admin_crud.update_user_board_permission(
        data_base=data_base,
        user_id=schema.user_id,
        board_id=schema.board_id,
        is_visible=schema.is_permitted,
    )


@router.put("/update_user_is_banned", status_code=status.HTTP_204_NO_CONTENT)
def update_user_is_banned(
    schema: admin_schema.UserBanOption,
    token: current_admin_payload,
    data_base: data_base_dependency,
):
    admin_crud.update_user_is_banned(
        data_base=data_base, user_id=schema.user_id, is_banned=schema.is_banned
    )


@router.post("/create_board", status_code=status.HTTP_204_NO_CONTENT)
def create_board(
    schema: admin_schema.BoradCreate,
    token: current_admin_payload,
    data_base: data_base_dependency,
):
    admin_crud.create_board(
        data_base=data_base,
        board_name=schema.name,
        board_information=schema.information,
        board_is_visible=schema.is_visible,
    )
