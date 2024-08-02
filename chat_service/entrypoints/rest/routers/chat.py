import os
import fastapi
import utils

from chat_service.bootstrap import bootstrap
from chat_service.services import views
from chat_service.entrypoints import schemas

config_path = utils.get_config_path()
config = utils.load_config(config_path)
router = fastapi.APIRouter()
bus = bootstrap()


@router.get("/chats")
async def get_chats(room_id: str) -> list[schemas.MessageResponse]:
    history = views.get_chat_history(room_id, bus.uow)
    return history


@router.get("/")
async def health_check():
    host = os.environ.get("HOST_URL", "localhost:8000")
    return fastapi.responses.HTMLResponse(
        f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chat</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: #f5f5f5;
        }}
        #chat {{
            width: 90%;
            max-width: 600px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
        }}
        #messages {{
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            margin-bottom: 10px;
        }}
        #messageInput {{
            width: calc(100% - 60px);
            padding: 10px;
        }}
        #sendButton {{
            width: 50px;
            padding: 10px;
        }}
        #roomInput {{
            margin-bottom: 10px;
            width: calc(100% - 22px);
            padding: 10px;
        }}
        button {{
            cursor: pointer;
        }}
    </style>
</head>
<body>

<div id="chat">
    <input type="text" id="roomInput" placeholder="Enter Room ID" />
    <button onclick="connectWebSocket()">Join Room</button>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Enter message" />
    <button id="sendButton" onclick="sendMessage()">Send</button>
</div>

<script>
    let ws;
    let roomId;

    function connectWebSocket() {{
        roomId = document.getElementById('roomInput').value;
        if (!roomId) {{
            alert("Please enter a room ID.");
            return;
        }}

        ws = new WebSocket(`ws://{host}/ws/${{roomId}}`);

        ws.onopen = function() {{
            console.log("Connected to WebSocket");
            fetchChatHistory();
        }};

        ws.onmessage = function(event) {{
            console.log(event.data);
            const messagesDiv = document.getElementById('messages');
            const data = JSON.parse(event.data);
            messagesDiv.innerHTML += `<div>${{data.username}}: ${{data.message}}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }};

        ws.onclose = function() {{
            console.log("Disconnected from WebSocket");
        }};

        ws.onerror = function(error) {{
            console.error("WebSocket error:", error);
        }};
    }}

    function sendMessage() {{
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value;
        if (ws && message) {{
            ws.send(message);
            messageInput.value = '';
        }}
    }}

    async function fetchChatHistory() {{
        try {{
            const response = await fetch(`http://{host}/chats?room_id=${{roomId}}`);
            const messages = await response.json();
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = messages.map(msg => `<div>${{msg.username}}: ${{msg.message}}</div>`).join('');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }} catch (error) {{
            console.error("Error fetching chat history:", error);
        }}
    }}
</script>

</body>
</html>

"""
    )
