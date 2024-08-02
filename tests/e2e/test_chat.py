from fastapi import testclient
import pytest
from chat_service.domains import commands
import core

from chat_service.services import views


def test_create_room(rest_client: testclient.TestClient):
    response = rest_client.post("/rooms", json={"password": "password1"})
    assert response.status_code == 201
    assert isinstance(response.json(), dict)
    assert "id" in response.json()


@pytest.fixture(scope="module")
def room_id(rest_client: testclient.TestClient) -> str:
    response = rest_client.post("/rooms", json={"password": "password1"})
    return response.json()["id"]


def test_send_chat(bus: core.MessageBus, room_id: str):
    cmd = commands.SendMessage(
        room_id=room_id,
        message="Hello",
        username="user1",
        image="image1",
    )
    bus.handle(cmd)


def test_get_chats(rest_client: testclient.TestClient, room_id: str):
    response = rest_client.get(
        "/chats", params={"room_id": room_id, "password": "password1"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_get_chats_wrong_password(rest_client: testclient.TestClient, room_id: str):
    response = rest_client.get(
        "/chats", params={"room_id": room_id, "password": "password2"}
    )
    assert response.status_code == 401


def test_get_chats_wrong_room(rest_client: testclient.TestClient, room_id: str):
    response = rest_client.get(
        "/chats", params={"room_id": room_id[::-1], "password": "password2"}
    )
    assert response.status_code == 404
