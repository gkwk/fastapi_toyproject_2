from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import get_data_base
from domain.board import board_crud, board_schema
from auth import (
    get_oauth2_scheme_admin,
    check_and_decode_admin_token,
    generate_admin_token,
    get_oauth2_scheme_user,
    generate_user_token,
    check_and_decode_user_token,
)

router = APIRouter(
    prefix="/api/board",
)


@router.get("/get_post/{board_id}/{post_id}", response_model=board_schema.PostRead)
def get_post(
    board_id: int,
    post_id: int,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    return board_crud.get_post_detail(data_base=data_base, post_id=post_id, board_id=board_id)


@router.get("/get_posts/{board_id}", response_model=board_schema.PostsRead)
def get_post(
    board_id: int,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    return board_crud.get_posts(data_base=data_base, board_id=board_id)


@router.post("/create_post", status_code=status.HTTP_204_NO_CONTENT)
def create_post(
    schema: board_schema.PostCreate,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    board_crud.create_post(data_base=data_base, schema=schema, token_payload=data)


@router.put("/update_post", status_code=status.HTTP_204_NO_CONTENT)
def update_post(
    schema: board_schema.PostUpdate,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    board_crud.update_post(data_base=data_base, schema=schema, token_payload=data)


@router.delete("/delete_post", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    schema: board_schema.PostDelete,
    token=Depends(get_oauth2_scheme_user()),
    data_base: Session = Depends(get_data_base),
):
    data = check_and_decode_user_token(token=token)
    board_crud.delete_post(data_base=data_base, schema=schema, token_payload=data)
