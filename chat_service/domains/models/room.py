import core
from .message import Message

__all__ = ["Room"]


class Room(core.BaseModel):
    """
    This class represents a message.
    """

    password: str
    messages: list[Message]

    def __init__(
        self,
        password: str,
        *args,
        **kwargs,
    ):
        self.password = password
        super().__init__(*args, **kwargs)
