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
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: #e9ecef;
        }}
        #chat {{
            width: 90%;
            max-width: 600px;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 30px;
            box-sizing: border-box;
        }}
        #messages {{
            height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 20px;
            background-color: #f8f9fa;
        }}
        #messageInput {{
            width: calc(100% - 70px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin-right: 10px;
        }}
        #roomInput, #roomPassword, #createRoomPassword {{
            margin-bottom: 15px;
            width: calc(100% - 22px);
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }}
        button {{
            cursor: pointer;
            padding: 10px 20px;
            background-color: #007bff;
            color: #ffffff;
            border: none;
            border-radius: 8px;
            transition: background-color 0.3s;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
        #sendButton {{
            padding: 10px;
        }}
        .form-group {{
            display: flex;
            align-items: center;
        }}
    </style>
</head>
<body>
<div id="instructions">
    <h1>WebSocket Chat</h1>

    <h2>Instructions</h2>
    <ol>
        <li>Click "Create room" to create a new chat room, you can provide a password if you want.</li>
        <li>Copy the room ID and share it along with the password (if any) with your friends.</li>
        <li>Enter the room ID and password (if any) and click "Connect" to join the chat room.</li>
        <li>Start chatting!</li>
    </ol>
</div>

<div id="chat">
    <input type="text" id="createRoomPassword" placeholder="(Optional) Password to Create Room" />
    <button onclick="createRoom()">Create Room</button>
    <input type="text" id="roomInput" placeholder="Enter Room ID" />
    <input type="text" id="roomPassword" placeholder="Enter Room Password" />
    <button onclick="connectWebSocket()">Connect</button>
    <div id="messages"></div>
    <div class="form-group">
        <input type="text" id="messageInput" placeholder="Enter Message" />
        <button id="sendButton" onclick="sendMessage()">Send</button>
    </div>
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
            messagesDiv.innerHTML += `<div><strong>${{data.username}}</strong>: ${{data.message}}</div>`;
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
                    messagesDiv.innerHTML += `<div><strong>${{message.username}}</strong>: ${{message.message}}</div>`;
                }});
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }})
            .catch(error => console.error("Error fetching chat history:", error));
    }}

    function createRoom() {{
        const createRoomPassword = document.getElementById('createRoomPassword');
        fetch('{http_url}/rooms', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify({{ password: createRoomPassword.value }})
        }})
        .then(response => response.json())
        .then(data => {{
            alert(`Room created with ID: ${{data.id}}`);
            createRoomPassword.value = '';
        }})
        .catch(error => console.error("Error creating room:", error));
    }}
</script>
</body>
</html>
"""
    )
