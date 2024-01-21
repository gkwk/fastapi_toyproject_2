import uuid
import json
from typing import Any, Dict

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/api/chat_test",
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


def chat_html(user_id, chat_id):
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
                var client_id = {user_id}
                document.querySelector("#ws-id").textContent = client_id;
                var ws = new WebSocket(`ws://localhost:8000/api/chat_test/ws/{chat_id}/{user_id}`);                
                
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


@router.get("/test/{chat_id}/{user_id}")
async def test(chat_id: int, user_id: int):
    print(manager.active_connections)
    return HTMLResponse(chat_html(user_id, chat_id))


# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: dict["WebSocket", int] = dict()

#     async def connect(self, websocket: WebSocket, client_id: int):
#         await websocket.accept()
#         self.active_connections[websocket] = client_id

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.pop(websocket)

#     async def send_personal_message(self, message: str, websocket: WebSocket):
#         await websocket.send_text(message)
#         print(self.active_connections)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)


# manager = ConnectionManager()


# def chat_html():
#     uuid_chat = uuid.uuid4().int
#     html = f"""
#     <!DOCTYPE html>
#     <html>
#         <head>
#             <title>Chat</title>
#         </head>
#         <body>
#             <h1>WebSocket Chat</h1>
#             <h2>Your ID: <span id="ws-id"></span></h2>
#             <form action="" onsubmit="sendMessage(event)">
#                 <input type="text" id="messageText" autocomplete="off"/>
#                 <button>Send</button>
#             </form>
#             <ul id='users'>
#             </ul>
#             <ul id='messages'>
#             </ul>
#             <script>
#                 var client_id = "{uuid_chat}"
#                 document.querySelector("#ws-id").textContent = client_id;
#                 var ws = new WebSocket(`ws://localhost:8000/api/chat_test/ws/${{client_id}}`);

#                 ws.onmessage = function(event) {{
#                     var jsonData = JSON.parse(event.data)

#                     if (jsonData.hasOwnProperty('message')) {{
#                         var messages = document.getElementById('messages')
#                         var message = document.createElement('li')
#                         var content = document.createTextNode(jsonData.message)
#                         message.appendChild(content)
#                         messages.appendChild(message)
#                     }}

#                     if (jsonData.hasOwnProperty('user_join')) {{
#                         var users = document.getElementById('users')
#                         var user = document.createElement('li')
#                         user.id = `${{jsonData.user_join}}`
#                         var content = document.createTextNode(jsonData.user_join)
#                         user.appendChild(content)
#                         users.appendChild(user)
#                     }}

#                     if (jsonData.hasOwnProperty('user_left')) {{
#                         var user = document.getElementById(`${{jsonData.user_left}}`)
#                         user.remove()
#                     }}
#                 }};
#                 function sendMessage(event) {{
#                     var input = document.getElementById("messageText")
#                     ws.send(JSON.stringify({{"message": input.value}}))
#                     input.value = ''
#                     event.preventDefault()
#                 }}
#             </script>
#         </body>
#     </html>
#     """
#     return html


# @router.get("/test")
# async def get():
#     print(manager.active_connections)
#     return HTMLResponse(chat_html())


# json_encoder = json.JSONEncoder()
# json_decoder = json.JSONDecoder()


# @router.websocket("/ws/{client_id}")
# async def websocket_endpoint(websocket: WebSocket, client_id: int):
#     await manager.connect(websocket, client_id)
#     try:
#         for i in manager.active_connections.values():
#             if i != client_id:
#                 await manager.send_personal_message(
#                     json_encoder.encode(o={"user_join": f"{i}"}), websocket
#                 )
#         await manager.broadcast(
#             json_encoder.encode(o={"message": f"Client #{client_id} joined the chat"})
#         )
#         await manager.broadcast(json_encoder.encode(o={"user_join": f"{client_id}"}))
#         while True:
#             data = await websocket.receive_text()
#             print(data, websocket)

#             data = json_decoder.decode(data)
#             message = data["message"]

#             await manager.send_personal_message(
#                 json_encoder.encode(o={"message": f"You wrote: {message}"}), websocket
#             )
#             await manager.broadcast(
#                 json_encoder.encode(
#                     o={"message": f"Client #{client_id} says: {message}"}
#                 )
#             )
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)
#         await manager.broadcast(json_encoder.encode(o={"user_left": f"{client_id}"}))
