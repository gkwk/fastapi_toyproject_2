import secrets
from datetime import datetime

from typing import List, Optional
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

user_chat_session_table = Table(
    "user_chat_session_table",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("chat_session_id", ForeignKey("chat_session.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[List["Post"]] = relationship(back_populates="user")  # 1 to N
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")  # 1 to N
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        secondary=user_chat_session_table, back_populates="users"
    )  # N to M
    chats: Mapped[List["Chat"]] = relationship(back_populates="user")  # 1 to N
    ai_logs: Mapped[List["AIlog"]] = relationship(back_populates="user")  # 1 to N

    name: Mapped[str] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String())
    password_salt: Mapped[str] = mapped_column(String(), default=secrets.token_hex(4))
    join_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
    is_superuser: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_banned: Mapped[Boolean] = mapped_column(Boolean(), default=False)


class Board(Base):
    __tablename__ = "board"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    information: Mapped[str] = mapped_column(String(512), unique=True)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class Post(Base):
    __tablename__ = "post"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[List["User"]] = relationship(back_populates="posts")

    name: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(String(1024))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime())
    number_of_view: Mapped[int] = mapped_column(Integer(), default=0)
    number_of_comment: Mapped[int] = mapped_column(Integer(), default=0)
    number_of_like: Mapped[int] = mapped_column(Integer(), default=0)
    is_file_attached: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="comments")
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    post: Mapped["Post"] = relationship(back_populates="comments")

    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime())
    is_file_attached: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class ChatSession(Base):
    __tablename__ = "chat_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    users: Mapped[List["User"]] = relationship(
        secondary=user_chat_session_table, back_populates="chat_sessions"
    )
    chats: Mapped[List["Chat"]] = relationship(back_populates="chat_session")

    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime())
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="chats")
    chat_session_id: Mapped[int] = mapped_column(ForeignKey("chat_session.id"))
    chat_session: Mapped["ChatSession"] = relationship(back_populates="chats")

    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class AI(Base):
    __tablename__ = "ai"

    id: Mapped[int] = mapped_column(primary_key=True)
    ai_logs: Mapped[List["AIlog"]] = relationship(back_populates="ai")

    name: Mapped[str] = mapped_column(String(64), unique=True)
    information: Mapped[str] = mapped_column(String(256))
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class AIlog(Base):
    __tablename__ = "ai_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="ai_logs")
    ai_id: Mapped[int] = mapped_column(ForeignKey("ai.id"))
    ai: Mapped[AI] = relationship(back_populates="ai_logs")

    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now())
    finish_date: Mapped[DateTime] = mapped_column(DateTime())
    is_finished: Mapped[Boolean] = mapped_column(Boolean(), default=True)
