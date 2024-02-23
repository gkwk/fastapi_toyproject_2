from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException, WebSocket
from starlette import status

from models import Chat, ChatSession, UserChatSessionTable
from auth import current_user_payload
from database import data_base_dependency


def create_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    name: str,
    information: str,
    is_visible: bool,
    is_closed: bool,
):
    chat_session = ChatSession(
        name=name,
        user_create_id=token.get("user_id"),
        information=information,
        is_visible=is_visible,
        is_closed=is_closed,
    )
    data_base.add(chat_session)
    data_base.commit()


def get_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    chatting_room_id: int,
):
    chat_session = data_base.query(ChatSession).filter_by(id=chatting_room_id).first()
    return chat_session


def get_chatsessions(
    data_base: data_base_dependency,
    token: current_user_payload,
    user_create_id: int | None,
    skip: int | None,
    limit: int | None,
):
    filter_kwargs = {}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    if token.get("is_admin"):
        if user_create_id != None:
            filter_kwargs["user_create_id"] = user_create_id
    else:
        filter_kwargs["user_create_id"] = user_create_id

    chat_sessions = (
        data_base.query(ChatSession)
        .filter_by(**filter_kwargs)
        .order_by(ChatSession.create_date.asc(), ChatSession.id.asc())
    )
    total = chat_sessions.count()
    chat_sessions = chat_sessions.offset(skip).limit(limit).all()
    return {"total": total, "chat_sessions": chat_sessions}


def update_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    name: str | None,
    information: str | None,
    is_visible: bool | None,
    is_closed: bool | None,
):
    chat_session = data_base.query(ChatSession).filter_by(id=id).first()

    if name != None:
        chat_session.name = name
    if information != None:
        chat_session.information = information
    if is_visible != None:
        chat_session.is_visible = is_visible
    if is_closed != None:
        chat_session.is_closed = is_closed

    data_base.add(chat_session)
    data_base.commit()


def delete_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
):
    chatsession = data_base.query(ChatSession).filter_by(id=id).first()
    data_base.delete(chatsession)
    data_base.commit()


def create_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    content: str,
    chat_session_id: int,
):
    chat = Chat(
        user_id=token.get("user_id"),
        chat_session_id=chat_session_id,
        content=content,
    )
    data_base.add(chat)
    data_base.commit()


def get_chats(
    data_base: data_base_dependency,
    token: current_user_payload,
    chat_session_id: int,
    skip: int | None,
    limit: int | None,
):
    filter_kwargs = {"chat_session_id": chat_session_id}

    if skip == None:
        skip = 0
    if limit == None:
        limit = 10

    chats = (
        data_base.query(Chat)
        .filter_by(**filter_kwargs)
        .order_by(Chat.create_date.asc(), Chat.id.asc())
    )
    total = chats.count()
    chats = chats.offset(skip).limit(limit).all()
    return {"total": total, "chats": chats}


def update_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    id: int,
    chat_session_id: int,
    content: str = None,
    is_visible: bool = None,
):
    chat = (
        data_base.query(Chat)
        .filter_by(
            id=id,
            user_id=token.get("user_id"),
            chat_session_id=chat_session_id,
        )
        .first()
    )

    if content != None:
        chat.content = content
    if is_visible != None:
        chat.is_visible = is_visible

    data_base.add(chat)
    data_base.commit()


def delete_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    chat_id: int,
    chatting_room_id: int,
):
    chat = (
        data_base.query(Chat)
        .filter_by(
            id=chat_id,
            user_id=token.get("user_id"),
            chat_session_id=chatting_room_id,
        )
        .first()
    )
    data_base.delete(chat)
    data_base.commit()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict["WebSocket", Dict[str, Any]]] = dict()
        self.active_user_id: Dict[int, Dict[int, "WebSocket"]] = dict()

    async def connect(self, websocket: WebSocket, chatting_room_id: int, user_id: int):
        if not chatting_room_id in self.active_connections:
            self.active_connections[chatting_room_id] = dict()

        if not user_id in self.active_user_id:
            self.active_user_id[user_id] = dict()

        if not chatting_room_id in self.active_user_id[user_id]:
            self.active_connections[chatting_room_id][websocket] = dict()
            self.active_connections[chatting_room_id][websocket]["user_id"] = user_id
            self.active_user_id[user_id][chatting_room_id] = websocket

            await websocket.accept()

    def disconnect(self, websocket: WebSocket, chatting_room_id: int, user_id: int):
        self.active_connections[chatting_room_id].pop(websocket)
        self.active_user_id[user_id].pop(chatting_room_id)
        websocket.close()

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, chatting_room_id: int):
        for connection in self.active_connections[chatting_room_id]:
            await connection.send_text(message)
