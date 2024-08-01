from datetime import datetime
import pydantic


class MessageResponse(pydantic.BaseModel):
    room_id: str
    message: str
    username: str
    image: str | None
    created_time: datetime
    updated_time: datetime
    id: str
