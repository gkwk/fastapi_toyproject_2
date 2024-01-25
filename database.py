from typing import Annotated, Optional
import contextlib

from fastapi import Depends
from sqlalchemy import create_engine, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from config import get_settings

import json


engine = create_engine(
    get_settings().SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# SQLite 버그 패치
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=naming_convention)


def database_engine_shutdown():
    global engine
    if engine:
        engine.dispose()


def get_data_base():
    data_base = session_local()
    try:
        yield data_base
    finally:
        data_base.close()


@contextlib.contextmanager
def get_data_base_for_decorator():
    data_base = session_local()
    try:
        yield data_base
    finally:
        data_base.close()


json_encoder = json.JSONEncoder()


def get_data_base_decorator(f):
    def wrapper(data_base, *args, **kwargs):
        with get_data_base_for_decorator() as data_base:
            if "data_base" in kwargs:
                kwargs["data_base"] = data_base
            f(data_base, *args, **kwargs)

    return wrapper


data_base_dependency = Annotated[Session, Depends(get_data_base)]
