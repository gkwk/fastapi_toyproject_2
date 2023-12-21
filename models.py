import secrets

from typing import List, Optional
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    email: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str]
    password_salt: Mapped[str] = mapped_column(String(), default=secrets.token_hex(4))
    join_date: Mapped[DateTime] = mapped_column(DateTime())
    is_superuser: Mapped[Boolean] = mapped_column(Boolean(), default=False)
    is_banned: Mapped[Boolean] = mapped_column(Boolean(), default=False)
