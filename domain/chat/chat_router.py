import uuid
import json

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from database import get_data_base
from domain.chat import *
from auth import (
    get_oauth2_scheme_v1,
    validate_and_decode_user_access_token,
    generate_access_token,
    get_oauth2_scheme_v1,
    generate_access_token,
    validate_and_decode_user_access_token,
)

router = APIRouter(
    prefix="/api/chat",
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict["WebSocket", int] = dict()

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections[websocket] = client_id

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


def chat_html():
    uuid_chat = uuid.uuid4().int
    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Chat</title>
        </head>
        <body>
            <h1>WebSocket Chat</h1>
            <h2>Your ID: <span id="ws-id"></span></h2>
            <form action="" onsubmit="sendMessage(event)">
                <input type="text" id="messageText" autocomplete="off"/>
                <button>Send</button>
            </form>
            <ul id='users'>
            </ul>
            <ul id='messages'>
            </ul>
            <script>
                var client_id = "{uuid_chat}"
                document.querySelector("#ws-id").textContent = client_id;
                var ws = new WebSocket(`ws://localhost:8000/api/chat/ws/${{client_id}}`);                
                
                ws.onmessage = function(event) {{
                    var jsonData = JSON.parse(event.data)
                    
                    if (jsonData.hasOwnProperty('message')) {{
                        var messages = document.getElementById('messages')
                        var message = document.createElement('li')
                        var content = document.createTextNode(jsonData.message)
                        message.appendChild(content)
                        messages.appendChild(message)
                    }}
                    
                    if (jsonData.hasOwnProperty('user_join')) {{
                        var users = document.getElementById('users')
                        var user = document.createElement('li')
                        user.id = `${{jsonData.user_join}}`
                        var content = document.createTextNode(jsonData.user_join)
                        user.appendChild(content)
                        users.appendChild(user)
                    }}
                    
                    if (jsonData.hasOwnProperty('user_left')) {{
                        var user = document.getElementById(`${{jsonData.user_left}}`)
                        user.remove()
                    }}
                }};
                function sendMessage(event) {{
                    var input = document.getElementById("messageText")
                    ws.send(JSON.stringify({{"message": input.value}}))
                    input.value = ''
                    event.preventDefault()
                }}
            </script>
        </body>
    </html>
    """
    return html


@router.get("/test")
async def get():
    print(manager.active_connections)
    return HTMLResponse(chat_html())


json_encoder = json.JSONEncoder()
json_decoder = json.JSONDecoder()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        for i in manager.active_connections.values():
            if i != client_id:
                await manager.send_personal_message(
                    json_encoder.encode(o={"user_join": f"{i}"}), websocket
                )
        await manager.broadcast(
            json_encoder.encode(o={"message": f"Client #{client_id} joined the chat"})
        )
        await manager.broadcast(json_encoder.encode(o={"user_join": f"{client_id}"}))
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
                    o={"message": f"Client #{client_id} says: {message}"}
                )
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json_encoder.encode(o={"user_left": f"{client_id}"}))
