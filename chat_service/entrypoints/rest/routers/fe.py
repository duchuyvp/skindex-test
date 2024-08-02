import os
import fastapi

from chat_service.entrypoints.rest import websocket
from chat_service.bootstrap import bootstrap

router = fastapi.APIRouter()
manager = websocket.ConnectionManager()
bus = bootstrap()


@router.get("/")
async def health_check():
    http_url = os.getenv("HTTP_URL", "http://localhost:8000")
    ws_url = os.getenv("WS_URL", "ws://localhost:8000")

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
        #roomInput, #roomPassword, #createRoomPassword {{
            margin-bottom: 10px;
            width: calc(100% - 22px);
            padding: 10px;
        }}
        button {{
            cursor: pointer;
            width: 50px;
            padding: 10px;
        }}
    </style>
</head>
<body>
<div id="chat">
    <input type="text" id="createRoomPassword" placeholder="(Optional) Password to Create Room" />
    <button onclick="createRoom()">Create Room</button>
    <input type="text" id="roomInput" placeholder="Enter Room ID" />
    <input type="text" id="roomPassword" placeholder="Enter Room Password" />
    <button onclick="connectWebSocket()">Connect</button>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Enter Message" />
    <button id="sendButton" onclick="sendMessage()">Send</button>
</div>

<script>
    let ws;
    let roomId;
    let roomPassword;

    function connectWebSocket() {{
        roomId = document.getElementById('roomInput').value;
        roomPassword = document.getElementById('roomPassword').value;
        if (!roomId) {{
            alert("Please enter a room ID and password.");
            return;
        }}
        ws = new WebSocket(`{ws_url}/ws/${{roomId}}?password=${{roomPassword}}`);
        ws.onopen = function(event) {{
            console.log('WebSocket connection established:', event);
            fetchChatHistory();
        }};
        ws.onmessage = function(event) {{
            console.log(event.data);
            const messagesDiv = document.getElementById('messages');
            const data = JSON.parse(event.data);
            messagesDiv.innerHTML += `<div>${{data.username}}: ${{data.message}}</div>`;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }};
        ws.onclose = function(event) {{
            console.log("Disconnected from WebSocket");
            if (event.code === 1000) {{
                alert(`Connection closed: ${{event.reason}}`);
            }} else {{
                console.error('Unexpected closure:', event);
            }}
        }};
        ws.onerror = function(error) {{
            console.log(error);
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

    function fetchChatHistory() {{
        fetch(`{http_url}/chats?room_id=${{roomId}}&password=${{roomPassword}}`)
            .then(response => response.json())
            .then(data => {{
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML = '';
                data.forEach(message => {{
                    messagesDiv.innerHTML += `<div>${{message.username}}: ${{message.message}}</div>`;
                }});
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }})
            .catch(error => console.error("Error fetching chat history:", error));
    }}

    function createRoom() {{
        const createRoomPassword = document.getElementById('createRoomPassword').value;
        fetch('http://localhost:8000/rooms', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{ password: createRoomPassword }})
        }})
        .then(response => response.json())
        .then(data => {{
            alert(`Room created with ID: ${{data.id}}`);
        }})
        .catch(error => console.error("Error creating room:", error));
    }}
</script>
</body>
</html>
"""
    )
