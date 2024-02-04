from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from database import data_base_dependency
from domain.board import board_crud, board_schema
from auth import current_user_payload

router = APIRouter(prefix="/board", tags=["board"])


@router.post("/create_post", status_code=status.HTTP_201_CREATED)
def create_post(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: board_schema.RequestPostCreate,
):
    board_crud.create_post(
        data_base=data_base,
        token=token,
        name=schema.name,
        board_id=schema.board_id,
        content=schema.content,
        is_file_attached=schema.is_file_attached,
        is_visible=schema.is_visible,
    )

    return {"result": "success"}


@router.get("/get_post/", response_model=board_schema.ResponsePostRead)
def get_post(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[board_schema.RequestPostRead, Depends()],
):
    return board_crud.get_post_detail(
        data_base=data_base,
        token=token,
        id=schema.id,
        board_id=schema.board_id,
    )


@router.get("/get_posts/", response_model=board_schema.ResponsePostsRead)
def get_posts(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[board_schema.RequestPostsRead, Depends()],
):
    return board_crud.get_posts(
        data_base=data_base,
        token=token,
        board_id=schema.board_id,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.put("/update_post", status_code=status.HTTP_204_NO_CONTENT)
def update_post(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: board_schema.RequestPostUpdate,
):
    board_crud.update_post(
        data_base=data_base,
        token=token,
        id=schema.id,
        board_id=schema.board_id,
        name=schema.name,
        content=schema.content,
        is_file_attached=schema.is_file_attached,
        is_visible=schema.is_visible,
    )


@router.delete("/delete_post", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema: Annotated[board_schema.RequestPostDelete, Depends()],
):
    board_crud.delete_post(
        data_base=data_base,
        token=token,
        id=schema.id,
        board_id=schema.board_id,
    )


@router.post("/create_comment", status_code=status.HTTP_201_CREATED)
def create_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: board_schema.RequestCommentCreate,
):
    board_crud.create_comment(
        data_base=data_base,
        token=token,
        post_id=schema.post_id,
        content=schema.content,
        is_file_attached=schema.is_file_attached,
        is_visible=schema.is_visible,
    )

    return {"result": "success"}

@router.get("/get_comment", response_model=board_schema.ResponseCommentRead)
def get_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[board_schema.RequestCommentRead, Depends()],
):
    return board_crud.get_comment_detail(
        data_base=data_base,
        token=token,
        id=schema.id,
        post_id=schema.post_id,
    )


@router.get("/get_comments", response_model=board_schema.ResponseCommentsRead)
def get_comments(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema: Annotated[board_schema.RequestCommentsRead, Depends()],
):
    return board_crud.get_comments(
        data_base=data_base,
        token=token,
        post_id=schema.post_id,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.put("/update_comment", status_code=status.HTTP_204_NO_CONTENT)
def update_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: board_schema.RequestCommentUpdate,
):
    board_crud.update_comment(
        data_base=data_base,
        token=token,
        id=schema.id,
        post_id=schema.post_id,
        content=schema.content,
        is_file_attached=schema.is_file_attached,
        is_visible=schema.is_visible,
    )


@router.delete("/delete_comment", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: Annotated[board_schema.CommentDelete, Depends()],
):
    board_crud.delete_comment(
        data_base=data_base,
        token=token,
        id=schema.id,
        post_id=schema.post_id,
    )
