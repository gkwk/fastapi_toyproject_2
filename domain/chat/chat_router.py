import uuid
import json
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import data_base_dependency
from domain.chat import chat_crud, chat_schema
from auth import current_user_payload
from models import ChatSession

router = APIRouter(
    prefix="/chat",
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


@router.post("/create_chatsession", status_code=status.HTTP_204_NO_CONTENT)
def create_comment(
    token: current_user_payload,
    data_base: data_base_dependency,
    content:str,
    is_visible:bool
    
):
    chat_crud.create_chatsession(data_base=data_base, token=token, content=content,is_visible=is_visible)





@router.websocket("/ws/chat/{chatting_room_id}/{user_id}")
async def websocket_test_endpoint(
    websocket: WebSocket,
    token: current_user_payload,
    data_base: data_base_dependency,
    chatting_room_id: int,
    user_id: int,
):
    if user_id == token.get("user_id"):
        await manager.connect(websocket, chatting_room_id, token.get("user_id"))
        try:
            for t_websocket in manager.active_connections[chatting_room_id]:
                t_user_id = manager.active_connections[chatting_room_id][t_websocket][
                    "user_id"
                ]
                if t_user_id != token.get("user_id"):
                    await manager.send_personal_message(
                        json_encoder.encode(o={"user_join": f"{t_user_id}"}), websocket
                    )

            for chat_query in chat_crud.get_chats(
                data_base=data_base,
                token=token,
                chatting_room_id=chatting_room_id,
                skip=0,
                limit=0,
            ).get("chats"):
                await manager.send_personal_message(
                    json_encoder.encode(o={"message": f"{chat_query.content}"}), websocket
                )

            await manager.broadcast(
                json_encoder.encode(
                    o={"message": f'Client #{token.get("user_id")} joined the chat'}
                ),
                chatting_room_id,
            )
            await manager.broadcast(
                json_encoder.encode(o={"user_join": f'{token.get("user_id")}'}),
                chatting_room_id,
            )
            while True:
                data = await websocket.receive_text()
                data = json_decoder.decode(data)
                message = data["message"]
                chat_crud.create_chat(
                    data_base=data_base,
                    token=token,
                    chat_content=message,
                    chatting_room_id=chatting_room_id,
                )

                await manager.send_personal_message(
                    json_encoder.encode(o={"message": f"You wrote: {message}"}),
                    websocket,
                )
                await manager.broadcast(
                    json_encoder.encode(
                        o={"message": f'Client #{token.get("user_id")} says: {message}'}
                    ),
                    chatting_room_id,
                )
        except WebSocketDisconnect:
            manager.disconnect(websocket, chatting_room_id, token.get("user_id"))
            await manager.broadcast(
                json_encoder.encode(o={"user_left": f'{token.get("user_id")}'}),
                chatting_room_id,
            )
        except Exception:
            print("Error")


# @router.websocket("/ws/test/{chatting_room_id}/{user_id}")
# async def websocket_test_endpoint(
#     websocket: WebSocket,
#     token: current_user_payload,
#     chatting_room_id: int,
#     user_id: int,
# ):
#     if user_id == token.get("user_id"):
#         await manager.connect(websocket, chatting_room_id, token.get("user_id"))
#         try:
#             for t_websocket in manager.active_connections[chatting_room_id]:
#                 t_user_id = manager.active_connections[chatting_room_id][t_websocket][
#                     "user_id"
#                 ]
#                 if t_user_id != token.get("user_id"):
#                     await manager.send_personal_message(
#                         json_encoder.encode(o={"user_join": f"{t_user_id}"}), websocket
#                     )
#             await manager.broadcast(
#                 json_encoder.encode(
#                     o={"message": f'Client #{token.get("user_id")} joined the chat'}
#                 ),
#                 chatting_room_id,
#             )
#             await manager.broadcast(
#                 json_encoder.encode(o={"user_join": f'{token.get("user_id")}'}),
#                 chatting_room_id,
#             )
#             while True:
#                 data = await websocket.receive_text()
#                 data = json_decoder.decode(data)
#                 message = data["message"]

#                 await manager.send_personal_message(
#                     json_encoder.encode(o={"message": f"You wrote: {message}"}),
#                     websocket,
#                 )
#                 await manager.broadcast(
#                     json_encoder.encode(
#                         o={"message": f'Client #{token.get("user_id")} says: {message}'}
#                     ),
#                     chatting_room_id,
#                 )
#         except WebSocketDisconnect:
#             manager.disconnect(websocket, chatting_room_id, token.get("user_id"))
#             await manager.broadcast(
#                 json_encoder.encode(o={"user_left": f'{token.get("user_id")}'}),
#                 chatting_room_id,
#             )
#         except Exception:
#             print("Error")
