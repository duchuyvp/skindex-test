from core import Command


class SendMessage(Command):
    """
    This class represents a command to send a message.
    """

    room_id: str
    message: str
    image: str | None
    username: str


class CreateRoom(Command):
    """
    This class represents a command to create a room.
    """

    password: str
