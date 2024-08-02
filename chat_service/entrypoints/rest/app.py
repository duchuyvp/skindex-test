import os
import fastapi
from fastapi.middleware import cors
import uvicorn

import utils
from chat_service.entrypoints.rest import routers


app = fastapi.FastAPI(root_path="/chat-service")

config_path = utils.get_config_path()
config = utils.load_config(config_path)

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routers.chat.router)
app.include_router(routers.ws.router)
app.include_router(routers.room.router)
app.include_router(routers.fe.router)


def run():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
