import uuid
import json
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import get_data_base
from domain.chat import *
from auth import (
    get_oauth2_scheme_admin,
    check_and_decode_admin_token,
    generate_admin_token,
    get_oauth2_scheme_user,
    generate_user_token,
    check_and_decode_user_token,
)

router = APIRouter(
    prefix="/api/chat",
)


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

        print(self.active_connections)
        print(self.active_user_id)

    def disconnect(self, websocket: WebSocket, chatting_room_id: int, user_id: int):
        self.active_connections[chatting_room_id].pop(websocket)
        self.active_user_id[user_id].pop(chatting_room_id)
        websocket.close()

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, chatting_room_id: int):
        for connection in self.active_connections[chatting_room_id]:
            await connection.send_text(message)


manager = ConnectionManager()
json_encoder = json.JSONEncoder()
json_decoder = json.JSONDecoder()


@router.websocket("/ws/{chatting_room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, chatting_room_id: int, user_id: int):
    await manager.connect(websocket, chatting_room_id, user_id)
    try:
        for for_websocket in manager.active_connections[chatting_room_id]:
            for_user_id = manager.active_connections[chatting_room_id][for_websocket][
                "user_id"
            ]
            if for_user_id != user_id:
                await manager.send_personal_message(
                    json_encoder.encode(o={"user_join": f"{for_user_id}"}), websocket
                )
        await manager.broadcast(
            json_encoder.encode(o={"message": f"Client #{user_id} joined the chat"}),
            chatting_room_id,
        )
        await manager.broadcast(
            json_encoder.encode(o={"user_join": f"{user_id}"}), chatting_room_id
        )
        while True:
            data = await websocket.receive_text()
            print(data, websocket)

            data = json_decoder.decode(data)
            message = data["message"]

            await manager.send_personal_message(
                json_encoder.encode(o={"message": f"You wrote: {message}"}), websocket
            )
            await manager.broadcast(
                json_encoder.encode(
                    o={"message": f"Client #{user_id} says: {message}"}
                ),
                chatting_room_id,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, chatting_room_id, user_id)
        await manager.broadcast(
            json_encoder.encode(o={"user_left": f"{user_id}"}), chatting_room_id
        )
    except Exception:
        print("Error")
