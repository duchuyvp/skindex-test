# WebSocket Chat API Documentation

## Overview

This WebSocket Chat API allows users to join a group chat and communicate in real-time. Users can connect to a chat room, send messages, and receive messages from other participants in the same room.

## Endpoints

### WebSocket Endpoint

- URL: ws://localhost:8000/ws/{room_id}
- Method: WebSocket
- Description: Connects to a WebSocket server for real-time communication in the specified chat room.

### REST Endpoint

- URL: <http://localhost:8000/chats?room_id={room_id}>
- Method: GET
- Description: Fetches the chat history for the specified chat room.

## WebSocket Connection

### Connecting to a WebSocket

To connect to a WebSocket, use the following JavaScript code:

```javascript
let ws;
let roomId;

function connectWebSocket() {
    roomId = document.getElementById('roomInput').value;
    if (!roomId) {
        alert("Please enter a room ID.");
        return;
    }
    ws = new WebSocket(`ws://localhost:8000/ws/${roomId}`);
    ws.onopen = function() {
        console.log("Connected to WebSocket");
        fetchChatHistory();
    };
    ws.onmessage = function(event) {
        console.log(event.data);
        const messagesDiv = document.getElementById('messages');
        const data = JSON.parse(event.data);
        messagesDiv.innerHTML += `<div>${data.username}: ${data.message}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };
    ws.onclose = function() {
        console.log("Disconnected from WebSocket");
    };
    ws.onerror = function(error) {
        console.error("WebSocket error:", error);
    };
}
```

### Sending Messages

To send a message over the WebSocket connection, use the following JavaScript code:

```javascript
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value;
    if (ws && message) {
        ws.send(message);
        messageInput.value = '';
    }
}
```

### Fetching Chat History

To fetch the chat history for a room, use the following JavaScript code:

```js
function fetchChatHistory() {
    const roomId = document.getElementById('roomInput').value;
    fetch(`http://localhost:8000/chats?room_id=${roomId}`)
        .then(response => response.json())
        .then(data => {
            const messagesDiv = document.getElementById('messages');
            messagesDiv.innerHTML = '';
            data.forEach(message => {
                messagesDiv.innerHTML += `<div>${message.username}: ${message.message}</div>`;
            });
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        })
        .catch(error => console.error("Error fetching chat history:", error));
}
```

## Usage

1. Connect to the WebSocket by calling the `connectWebSocket` function.
2. Fetch chat history by calling the `fetchChatHistory` function.
3. Send messages by typing in the message input and clicking the send button.

## Example

Here is an example of how to use the WebSocket Chat API:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WebSocket Chat</title>
</head>
<body>
    <input type="text" id="roomInput" placeholder="Enter Room ID">
    <button onclick="connectWebSocket()">Connect</button>
    <div id="messages" style="height: 300px; overflow-y: scroll;"></div>
    <input type="text" id="messageInput" placeholder="Enter Message">
    <button onclick="sendMessage()">Send</button>

    <script>
        // JavaScript code from above
    </script>
</body>
</html>
```

## Conclusion

This documentation provides an overview of how to connect to the WebSocket chat API, send messages, and fetch chat history. Use the provided examples to integrate the chat functionality into your application.
