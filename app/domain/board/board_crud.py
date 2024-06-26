from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from fastapi import UploadFile

from models import Post, User, Board, Comment, PostFile, CommentFile, PostViewIncrement
from domain.board import board_schema
from database import data_base_dependency
from auth import current_user_payload
from http_execption_params import http_exception_params

def create_post(
    data_base: data_base_dependency,
    token: current_user_payload,
    name: str,
    board_id: int,
    content: str,
    is_file_attached: bool,
    is_visible: bool,
    files: list[UploadFile],
):
    post: Post = Post(
        name=name,
        user_id=token.get("user_id"),
        board_id=board_id,
        content=content,
        is_file_attached=is_file_attached,
        is_visible=is_visible,
    )
    data_base.add(post)
    data_base.commit()

    if files != None:
        for i, file in enumerate(files):
            if file != None:
                file_uuid_name = str(uuid.uuid4())
                file_path = f"staticfile/{file_uuid_name}_{file.filename}"
                with open(file_path, "wb+") as file_object:
                    file_object.write(file.file.read())
                    post_file = PostFile(
                        post_id=post.id,
                        board_id=board_id,
                        file_uuid_name=file_uuid_name,
                        file_original_name=file.filename,
                        file_path=file_path,
                    )
                    data_base.add(post_file)
                    data_base.commit()

    return post.id


def get_posts(
    data_base: data_base_dependency,
    token: current_user_payload,
    board_id: int,
    skip: int | None,
    limit: int | None,
):
    filter_kwargs = {"board_id": board_id}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    posts = (
        data_base.query(Post)
        .filter_by(**filter_kwargs)
        .order_by(Post.create_date.desc(), Post.id.desc())
    )
    total = posts.count()
    posts = posts.offset(skip).limit(limit).all()

    return {"total": total, "posts": posts}


def record_post_view(data_base: data_base_dependency, post_id: int):
    post_view_increment: PostViewIncrement = PostViewIncrement(
        post_id=post_id,
    )
    data_base.add(post_view_increment)
    data_base.commit()


def get_post_detail(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    board_id: int,
):
    record_post_view(data_base=data_base, post_id=id)
    return data_base.query(Post).filter_by(id=id, board_id=board_id).first()


def update_post(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    board_id: int,
    name: str | None,
    content: str | None,
    is_file_attached: bool | None,
    is_visible: bool | None,
):
    post = (
        data_base.query(Post)
        .filter_by(
            id=id,
            user_id=token.get("user_id"),
            board_id=board_id,
        )
        .first()
    )

    if name != None:
        post.name = name
    if content != None:
        post.content = content
    if is_file_attached != None:
        post.is_file_attached = is_file_attached
    if is_visible != None:
        post.is_visible = is_visible

    data_base.add(post)
    data_base.commit()


def delete_post(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    board_id: int,
):
    post = (
        data_base.query(Post)
        .filter_by(
            id=id,
            user_id=token.get("user_id"),
            board_id=board_id,
        )
        .first()
    )
    data_base.delete(post)
    data_base.commit()


def create_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    post_id: int,
    content: str,
    is_file_attached: bool,
    is_visible: bool,
    files: list[UploadFile],
):
    comment = Comment(
        user_id=token.get("user_id"),
        post_id=post_id,
        content=content,
        is_file_attached=is_file_attached,
        is_visible=is_visible,
    )
    data_base.add(comment)
    data_base.commit()

    if files != None:
        for i, file in enumerate(files):
            if file != None:
                file_uuid_name = str(uuid.uuid4())
                file_path = f"staticfile/{file_uuid_name}_{file.filename}"
                with open(file_path, "wb+") as file_object:
                    file_object.write(file.file.read())
                    comment_file = CommentFile(
                        comment_id=comment.id,
                        post_id=post_id,
                        file_uuid_name=file_uuid_name,
                        file_original_name=file.filename,
                        file_path=file_path,
                    )
                    data_base.add(comment_file)
                    data_base.commit()

    return comment.id


def get_comments(
    data_base: data_base_dependency,
    token: current_user_payload,
    post_id: int,
    skip: int | None,
    limit: int | None,
):
    filter_kwargs = {"post_id": post_id}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    comments = (
        data_base.query(Comment)
        .filter_by(**filter_kwargs)
        .order_by(Comment.create_date.desc(), Comment.id.desc())
    )
    total = comments.count()
    comments = comments.offset(skip).limit(limit).all()

    return {"total": total, "comments": comments}


def get_comment_detail(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    post_id: int,
):
    comment_detail = data_base.query(Comment).filter_by(id=id, post_id=post_id).first()

    return comment_detail


def update_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    post_id: int,
    content: str | None,
    is_file_attached: bool | None,
    is_visible: bool | None,
):
    comment = (
        data_base.query(Comment)
        .filter_by(
            id=id,
            user_id=token.get("user_id"),
            post_id=post_id,
        )
        .first()
    )

    if content != None:
        comment.content = content
    if is_file_attached != None:
        comment.is_file_attached = is_file_attached
    if is_visible != None:
        comment.is_visible = is_visible

    data_base.add(comment)
    data_base.commit()


def delete_comment(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    post_id: int,
):
    comment = (
        data_base.query(Comment)
        .filter_by(
            id=id,
            user_id=token.get("user_id"),
            post_id=post_id,
        )
        .first()
    )
    data_base.delete(comment)
    data_base.commit()
