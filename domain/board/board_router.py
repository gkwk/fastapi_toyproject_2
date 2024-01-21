from fastapi import APIRouter
from starlette import status

from database import data_base_dependency
from domain.board import board_crud, board_schema
from auth import current_user_payload

router = APIRouter(
    prefix="/board",
)


@router.get("/get_post/{board_id}/{post_id}", response_model=board_schema.PostRead)
def get_post(
    board_id: int,
    post_id: int,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    return board_crud.get_post_detail(
        data_base=data_base, post_id=post_id, board_id=board_id
    )


@router.get("/get_posts/{board_id}", response_model=board_schema.PostsRead)
def get_posts(
    token: current_user_payload,
    data_base: data_base_dependency,
    board_id: int,
    skip: int = 10,
    limit: int = 20,
):
    return board_crud.get_posts(
        data_base=data_base, board_id=board_id, skip=skip, limit=limit
    )


@router.post("/create_post", status_code=status.HTTP_204_NO_CONTENT)
def create_post(
    schema: board_schema.PostCreate,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    board_crud.create_post(data_base=data_base, schema=schema, token_payload=token)


@router.put("/update_post", status_code=status.HTTP_204_NO_CONTENT)
def update_post(
    schema: board_schema.PostUpdate,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    board_crud.update_post(data_base=data_base, schema=schema, token_payload=token)


@router.delete("/delete_post", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    schema: board_schema.PostDelete,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    board_crud.delete_post(data_base=data_base, schema=schema, token_payload=token)


@router.get(
    "/get_comment/{post_id}/{comment_id}", response_model=board_schema.CommentRead
)
def get_comment(
    post_id: int,
    comment_id: int,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    return board_crud.get_comment_detail(
        data_base=data_base, post_id=post_id, comment_id=comment_id
    )


@router.get("/get_comments/{post_id}", response_model=board_schema.CommentsRead)
def get_comments(
    token: current_user_payload,
    data_base: data_base_dependency,
    post_id: int,
    skip: int = 0,
    limit: int = 10,
):
    return board_crud.get_comments(
        data_base=data_base, post_id=post_id, skip=skip, limit=limit
    )


@router.post("/create_comment", status_code=status.HTTP_204_NO_CONTENT)
def create_comment(
    schema: board_schema.CommentCreate,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    board_crud.create_comment(data_base=data_base, schema=schema, token_payload=token)


@router.put("/update_comment", status_code=status.HTTP_204_NO_CONTENT)
def update_comment(
    schema: board_schema.CommentUpdate,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    board_crud.update_comment(data_base=data_base, schema=schema, token_payload=token)


@router.delete("/delete_comment", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    schema: board_schema.CommentDelete,
    token: current_user_payload,
    data_base: data_base_dependency,
):
    board_crud.delete_comment(data_base=data_base, schema=schema, token_payload=token)
