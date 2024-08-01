import core

__all__ = ["Message"]


class Message(core.BaseModel):
    """
    This class represents a message.
    """

    room_id: str
    message: str
    image: str | None
    username: str

    def __init__(
        self,
        room_id: str,
        message: str,
        image: str | None,
        username: str,
        *args,
        **kwargs,
    ):
        self.room_id = room_id
        self.message = message
        self.image = image
        self.username = username
        super().__init__(*args, **kwargs)
