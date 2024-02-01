from datetime import datetime
import inspect

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
    BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

user_chat_session_table = Table(
    "user_chat_session_table",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("chat_session_id", ForeignKey("chat_session.id"), primary_key=True),
)

# user_permisson_table = Table(
#     "user_board_table",
#     Base.metadata,
#     Column("user_id", ForeignKey("user.id"), primary_key=True),
#     Column("board_id", ForeignKey("board.id"), primary_key=True),
# )

class UserPermissionTable(Base):
    __tablename__ = "user_board_table"
    # __table_args__ = {"sqlite_autoincrement": True}
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("board.id"), primary_key=True)




class User(Base):
    __tablename__ = "user"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[List["Post"]] = relationship(back_populates="user")  # 1 to N
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")  # 1 to N
    chat_sessions: Mapped[List["ChatSession"]] = relationship(
        secondary=user_chat_session_table, back_populates="users"
    )  # N to M
    boards: Mapped[List["Board"]] = relationship(
        secondary="user_board_table", back_populates="users"
    )  # N to M
    chats: Mapped[List["Chat"]] = relationship(back_populates="user")  # 1 to N
    ai_logs: Mapped[List["AIlog"]] = relationship(back_populates="user", cascade="all, delete")  # 1 to N

    name: Mapped[str] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String())
    password_salt: Mapped[str] = mapped_column(String())
    join_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    is_superuser: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_banned: Mapped[Boolean] = mapped_column(Boolean(), default=False)


class Board(Base):
    __tablename__ = "board"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    users: Mapped[List["User"]] = relationship(
        # class는 table명을 사용한다. class 아닌 table을 사용하면 table 변수를 사용한다. 
        secondary="user_board_table", back_populates="boards"
    )  # N to M
    posts: Mapped[List["Post"]] = relationship(back_populates="board")  # 1 to N
    information: Mapped[str] = mapped_column(String(512))
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class Post(Base):
    __tablename__ = "post"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="posts")
    board_id: Mapped[int] = mapped_column(ForeignKey("board.id"))
    board: Mapped["Board"] = relationship(back_populates="posts")
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")

    name: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(String(1024))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime())
    number_of_view: Mapped[int] = mapped_column(Integer(), default=0)
    number_of_comment: Mapped[int] = mapped_column(Integer(), default=0)
    number_of_like: Mapped[int] = mapped_column(Integer(), default=0)
    is_file_attached: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class Comment(Base):
    __tablename__ = "comment"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="comments")
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    post: Mapped["Post"] = relationship(back_populates="comments")

    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime())
    is_file_attached: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class ChatSession(Base):
    __tablename__ = "chat_session"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    users: Mapped[List["User"]] = relationship(
        secondary=user_chat_session_table, back_populates="chat_sessions"
    )
    chats: Mapped[List["Chat"]] = relationship(back_populates="chat_session")

    name: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime())
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)
    is_closed: Mapped[Boolean] = mapped_column(Boolean(), default=False)


class Chat(Base):
    __tablename__ = "chat"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="chats")
    chat_session_id: Mapped[int] = mapped_column(ForeignKey("chat_session.id"))
    chat_session: Mapped["ChatSession"] = relationship(back_populates="chats")


    content: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(), default=None, onupdate=datetime.now)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=True)


class AI(Base):
    __tablename__ = "ai"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    ai_logs: Mapped[List["AIlog"]] = relationship(back_populates="ai", cascade="all, delete")

    name: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(), default=None, onupdate=datetime.now)
    finish_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(), default=None)
    is_visible: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_available: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    celery_task_id : Mapped[str] = mapped_column(String(64))


class AIlog(Base):
    __tablename__ = "ai_log"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="ai_logs")
    ai_id: Mapped[int] = mapped_column(ForeignKey("ai.id"))
    ai: Mapped[AI] = relationship(back_populates="ai_logs")

    description: Mapped[str] = mapped_column(String(256))
    result: Mapped[str] = mapped_column(String(256))
    create_date: Mapped[DateTime] = mapped_column(DateTime(), default=datetime.now)
    update_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(), default=None, onupdate=datetime.now)
    finish_date: Mapped[Optional[DateTime]] = mapped_column(DateTime(), default=None)
    is_finished: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    celery_task_id : Mapped[str] = mapped_column(String(64))