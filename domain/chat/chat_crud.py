from sqlalchemy.orm import Session
from datetime import datetime

from models import Chat, ChatSession


from datetime import datetime
import secrets

from fastapi import HTTPException
from starlette import status

from models import User
from domain.user.user_schema import (
    UserCreate,
    UserUpdate,
    UserUpdatePassword,
)
from auth import get_password_context, current_user_payload
from database import data_base_dependency

def create_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    content: str,
    is_visible: bool,
): 
    chat_session = ChatSession(
        content=content,
        is_visible=is_visible,
    )
    data_base.add(chat_session)
    data_base.commit()




def create_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    chat_content: str,
    chatting_room_id: int,
):
    chat = Chat(
        user_id=token.get("user_id"),
        chat_session_id=chatting_room_id,
        content=chat_content,
    )
    data_base.add(chat)
    data_base.commit()


def get_chats(
    data_base: data_base_dependency,
    token: current_user_payload,
    chatting_room_id: int,
    skip: int,
    limit: int,
):
    chats = (
        data_base.query(Chat)
        .filter_by(chat_session_id=chatting_room_id)
        .order_by(Chat.create_date.asc(), Chat.id.asc())
    )
    total = chats.count()
    # chats = chats.offset(skip).limit(limit).all()
    chats = chats.all()
    return {"total": total, "chats": chats}
