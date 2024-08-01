from fastapi import testclient
from chat_service.domains import commands
import core


def test_send_chat(bus: core.MessageBus):
    cmd = commands.SendMessage(
        room_id="room1",
        message="Hello",
        username="user1",
        image="image1",
    )
    bus.handle(cmd)


def test_get_chats(rest_client: testclient.TestClient):
    response = rest_client.get("/chats", params={"room_id": "room1"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1
