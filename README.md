# Chat Service API Documentation

## Overview

The Chat Service API provides endpoints to manage chat rooms, handle WebSocket connections, and perform various chat-related operations. This documentation includes setup instructions, endpoint descriptions, and usage examples.

## Setup

### Prerequisites

- Git
- Docker and Docker Compose

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/duchuyvp/skindex-test
    cd skindex-test
    ```

2. Edit `.configs/database.yaml` to configure the database connection. I recommend leave it there to using the default values.

3. Start the application:

    ```bash
    docker-compose up -d
    ```

4. Application is now running on `http://localhost:8000`.

## Endpoints

### Health Check

- URL: `/`
- Description: Check the health of the application.
- Method: GET
- Response

  - `200 OK`: The application is healthy.

### Create Chat Room

- URL: `/rooms`
- Description: Create a new chat room.
- Method: POST
- Request Body

  - `password` (string) (Optional): The password to protect the chat room. It's used to join the chat room.

- Response

  - `201 Created`:  The chat room is created successfully.

      ```json
      {
          "id": "string",
          "created_time": "string",
      }
      ```

  - `422 Unprocessable Entity`: The request body is invalid.

      ```json
      {
          "detail": [
              {
              "type": "string_type",
              "loc": [
                  "body",
                  "password"
              ],
              "msg": "Input should be a valid string",
              "input": 123
              }
          ]
      }
      ```

### Retrive messages of room

- URL: `/chats`
- Description: Get message of room.
- Method: GET
- Request param

  - `room_id` (string): The id of room.
  - `password` (string) (Optional): The password to join the chat room. No need for rooms created with empty password.

- Response

  - `200 OK`: Retrive messages of room successfully.

      ```json
      [
        {
          "room_id": "string",
          "message": "string",
          "username": "string",
          "image": "string or null",
          "created_time": "string",
          "updated_time": "string",
          "id": "string"
        }
      ]
      ```

  - `401 Unauthorized`: Invalid password for the room

      ```json
      {
        "detail": "Invalid password for the room"
      }
      ```

  - `404 Not Found`: Room not found

      ```json
      {
        "detail": "Room not found"
      }
      ```

### Websocket connection

- URL: `/ws/{room_id}`
- Description: Connect to the chat room via WebSocket.
- Method: WebSocket
- Path parameter

  - `room_id` (string): The id of room.

## Usage Examples

### Create Chat Room

```bash
curl -X 'POST' \
  'http://localhost:8000/rooms' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"password": "string"}'
```

```
{"created_time":"2024-08-02T21:12:17.860537","id":"244f115b-da8a-417f-b77d-367b5fea5852"}
```

### Websocket connection

```bash
# apt update
# apt install nodejs npm -y
# npm install -g wscat
wscat -c 'ws://127.0.0.1:8000/ws/244f115b-da8a-417f-b77d-367b5fea5852?password=string'

> Hello, server!

```

### Retrive messages of room

```bash
curl -X 'GET' 'http://localhost:8000/chats?room_id=244f115b-da8a-417f-b77d-367b5fea5852&password=string'
```

```json
[
  {
    "room_id":"244f115b-da8a-417f-b77d-367b5fea5852",
    "message":"Hello, server!",
    "username":"Anonymous",
    "image":null,
    "created_time":"2024-08-02T21:23:07.043207",
    "updated_time":"2024-08-02T21:23:07.043209",
    "id":"bd980326-9184-4ce6-a263-76c4e5d12df5"
  }
]
```

## Conclusion

This documentation provides a comprehensive guide to setting up and using the Chat Service API. For further details, refer to the source code and comments within the project.
