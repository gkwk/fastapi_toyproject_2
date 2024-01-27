import json

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette import status

from database import data_base_dependency
from domain.chat import chat_crud, chat_schema
from auth import current_user_payload

router = APIRouter(
    prefix="/chat",
)


manager = chat_crud.ConnectionManager()
json_encoder = json.JSONEncoder()
json_decoder = json.JSONDecoder()


@router.post("/create_chatsession", status_code=status.HTTP_204_NO_CONTENT)
def create_chatsession(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatSessionCreate,
):
    chat_crud.create_chatsession(
        data_base=data_base, token=token, content=schema.content, is_visible=schema.is_visible
    )


@router.post("/get_chatsession")
def get_chatsession(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatSessionRead,
):
    return chat_crud.get_chatsession(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
    )


@router.post("/get_chatsessions")
def get_chatsessions(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatSessionsRead,
):
    return chat_crud.get_chatsessions(
        data_base=data_base, token=token, skip=schema.skip, limit=schema.limit
    )


@router.post("/update_chatsession", status_code=status.HTTP_204_NO_CONTENT)
def update_chatsession(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatSessionUpdate,
):
    chat_crud.update_chatsession(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
        content=schema.content,
        is_visible=schema.is_visible,
    )


@router.post("/delete_chatsession", status_code=status.HTTP_204_NO_CONTENT)
def delete_chatsession(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatSessionDelete,
):
    chat_crud.delete_chatsession(
        data_base=data_base, token=token, chatting_room_id=schema.chatting_room_id
    )


@router.post("/create_chat", status_code=status.HTTP_204_NO_CONTENT)
def create_chat(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatCreate,
):
    chat_crud.create_chat(
        data_base=data_base,
        token=token,
        chat_content=schema.chat_content,
        chatting_room_id=schema.chatting_room_id,
    )


@router.post("/get_chats")
def get_chats(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatsRead,
):
    return chat_crud.get_chats(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.post("/update_chat", status_code=status.HTTP_204_NO_CONTENT)
def update_chat(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatUpdate,
):
    chat_crud.update_chat(
        data_base=data_base,
        token=token,
        chat_id=schema.chat_id,
        chatting_room_id=schema.chatting_room_id,
        content=schema.content,
        is_visible=schema.is_visible,
    )


@router.post("/delete_chat", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    token: current_user_payload,
    data_base: data_base_dependency,
    schema : chat_schema.ChatDelete,
):
    chat_crud.delete_chat(
        data_base=data_base,
        token=token,
        chat_id=schema.chat_id,
        chatting_room_id=schema.chatting_room_id,
    )


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
                    json_encoder.encode(o={"message": f"{chat_query.content}"}),
                    websocket,
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
