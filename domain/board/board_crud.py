from sqlalchemy.orm import Session
from datetime import datetime

from models import Post, User, Board, Comment
from domain.board.board_schema import (
    PostCreate,
    PostUpdate,
    PostDelete,
    CommentCreate,
    CommentUpdate,
    CommentDelete,
)


def get_posts(data_base: Session, board_id: int, skip: int, limit: int):
    posts = (
        data_base.query(Post)
        .filter_by(board_id=board_id)
        .order_by(Post.create_date.desc(), Post.id.desc())
    )
    total = posts.count()
    posts = posts.offset(skip).limit(limit).all()

    return {"total": total, "posts": posts}


def get_post_detail(data_base: Session, post_id: int, board_id: int):
    return data_base.query(Post).filter_by(id=post_id, board_id=board_id).first()


def create_post(data_base: Session, schema: PostCreate, token_payload: dict):
    post: Post = Post(
        name=schema.name,
        user_id=token_payload["user_id"],
        board_id=schema.board_id,
        content=schema.content,
        is_file_attached=schema.is_file_attached,
        is_visible=schema.is_visible,
    )
    data_base.add(post)
    data_base.commit()


def update_post(data_base: Session, schema: PostUpdate, token_payload: dict):
    post = (
        data_base.query(Post)
        .filter_by(
            id=schema.id,
            user_id=token_payload["user_id"],
            board_id=schema.board_id,
        )
        .first()
    )

    post.name = schema.name
    post.content = schema.content
    post.update_date = datetime.now()
    post.is_file_attached = schema.is_file_attached
    post.is_visible = schema.is_visible
    data_base.add(post)
    data_base.commit()


def delete_post(data_base: Session, schema: PostDelete, token_payload: dict):
    post = (
        data_base.query(Post)
        .filter_by(
            id=schema.id,
            user_id=token_payload["user_id"],
            board_id=schema.board_id,
        )
        .first()
    )
    data_base.delete(post)
    data_base.commit()


def get_comments(data_base: Session, post_id: int, skip: int, limit: int):
    comments = (
        data_base.query(Comment)
        .filter_by(post_id=post_id)
        .order_by(Comment.create_date.desc(), Comment.id.desc())
    )
    total = comments.count()
    comments = comments.offset(skip).limit(limit).all()

    return {"total": total, "comments": comments}


def get_comment_detail(data_base: Session, comment_id: int, post_id: int):
    comment_detail = (
        data_base.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
    )

    return comment_detail


def create_comment(data_base: Session, schema: CommentCreate, token_payload: dict):
    post = Comment(
        user_id=token_payload["user_id"],
        post_id=schema.post_id,
        content=schema.content,
        is_file_attached=schema.is_file_attached,
        is_visible=schema.is_visible,
    )
    data_base.add(post)
    data_base.commit()


def update_comment(data_base: Session, schema: CommentUpdate, token_payload: dict):
    comment = (
        data_base.query(Comment)
        .filter_by(
            id=schema.id,
            user_id=token_payload["user_id"],
            post_id=schema.post_id,
        )
        .first()
    )

    comment.content = schema.content
    comment.update_date = datetime.now()
    comment.is_file_attached = schema.is_file_attached
    comment.is_visible = schema.is_visible
    data_base.add(comment)
    data_base.commit()


def delete_comment(data_base: Session, schema: CommentDelete, token_payload: dict):
    comment = (
        data_base.query(Comment)
        .filter_by(
            id=schema.id,
            user_id=token_payload["user_id"],
            post_id=schema.post_id,
        )
        .first()
    )
    data_base.delete(comment)
    data_base.commit()
