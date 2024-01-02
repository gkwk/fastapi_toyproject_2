from sqlalchemy.orm import Session
from datetime import datetime

from models import Post, User, Board
from domain.board.board_schema import PostCreate, PostUpdate, PostDelete


def get_posts(data_base: Session, board_id: int, skip: int = 0, limit: int = 10):
    posts = (
        data_base.query(Post)
        .filter_by(board_id=board_id)
        .order_by(Post.create_date.desc(), Post.id.desc())
    )
    total = posts.count()
    posts = posts.offset(skip).limit(limit).all()

    return {"total": total, "posts": posts}


def get_post_detail(data_base: Session, post_id: int, board_id: int):
    post_detail = data_base.query(Post).filter_by(id=post_id, board_id=board_id).first()

    return post_detail


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
