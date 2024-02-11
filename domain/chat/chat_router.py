import json

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from starlette import status

from database import data_base_dependency
from domain.chat import chat_crud, chat_schema
from auth import current_user_payload
import v1_urn

router = APIRouter(prefix=v1_urn.CHAT_PREFIX, tags=["chat"])


manager = chat_crud.ConnectionManager()
json_encoder = json.JSONEncoder()
json_decoder = json.JSONDecoder()


@router.post(v1_urn.CHAT_CREATE_CHATSESSION, status_code=status.HTTP_204_NO_CONTENT)
def create_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatSessionCreate,
):
    chat_crud.create_chatsession(
        data_base=data_base,
        token=token,
        content=schema.content,
        is_visible=schema.is_visible,
    )


@router.get(v1_urn.CHAT_GET_CHATSESSION)
def get_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatSessionRead,
):
    return chat_crud.get_chatsession(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
    )


@router.get(v1_urn.CHAT_GET_CHATSESSIONS)
def get_chatsessions(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatSessionsRead,
):
    return chat_crud.get_chatsessions(
        data_base=data_base,
        token=token,
        user_id=schema.user_id,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.put(v1_urn.CHAT_UPDATE_CHATSESSION, status_code=status.HTTP_204_NO_CONTENT)
def update_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatSessionUpdate,
):
    chat_crud.update_chatsession(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
        content=schema.content,
        is_visible=schema.is_visible,
    )


@router.delete(v1_urn.CHAT_DELETE_CHATSESSION, status_code=status.HTTP_204_NO_CONTENT)
def delete_chatsession(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatSessionDelete,
):
    chat_crud.delete_chatsession(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
    )


@router.post(v1_urn.CHAT_CREATE_CHAT, status_code=status.HTTP_204_NO_CONTENT)
def create_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatCreate,
):
    chat_crud.create_chat(
        data_base=data_base,
        token=token,
        chat_content=schema.chat_content,
        chatting_room_id=schema.chatting_room_id,
    )


@router.get(v1_urn.CHAT_GET_CHATS)
def get_chats(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatsRead,
):
    return chat_crud.get_chats(
        data_base=data_base,
        token=token,
        chatting_room_id=schema.chatting_room_id,
        skip=schema.skip,
        limit=schema.limit,
    )


@router.put(v1_urn.CHAT_UPDATE_CHAT, status_code=status.HTTP_204_NO_CONTENT)
def update_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatUpdate,
):
    chat_crud.update_chat(
        data_base=data_base,
        token=token,
        chat_id=schema.chat_id,
        chatting_room_id=schema.chatting_room_id,
        content=schema.content,
        is_visible=schema.is_visible,
    )


@router.delete(v1_urn.CHAT_DELETE_CHAT, status_code=status.HTTP_204_NO_CONTENT)
def delete_chat(
    data_base: data_base_dependency,
    token: current_user_payload,
    schema: chat_schema.RequestChatDelete,
):
    chat_crud.delete_chat(
        data_base=data_base,
        token=token,
        chat_id=schema.chat_id,
        chatting_room_id=schema.chatting_room_id,
    )


@router.websocket(v1_urn.CHAT_WEBSOCKET)
async def websocket_test_endpoint(
    websocket: WebSocket,
    data_base: data_base_dependency,
    token: current_user_payload,
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
