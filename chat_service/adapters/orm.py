import logging
from typing import Any

import core
import sqlalchemy as sa
import utils
from core.adapters import create_component_factory, sqlalchemy_adapter
from core.orm import map_once
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    event,
    orm as sqlalchemy_orm,
    String,
    Table,
    Text,
)

from chat_service.domains import models
from chat_service.entrypoints import schemas

config = utils.get_config()
logger = logging.getLogger(__name__)


def setup_model_on_callbacks():
    def set_in_memory_attributes(obj: core.BaseModel, _):
        obj.load_from_database()

    for model in [models.Message]:
        event.listen(model, "load", set_in_memory_attributes)


component_factory = create_component_factory(config["database"])
assert isinstance(component_factory, sqlalchemy_adapter.ComponentFactory)

registry = component_factory.create_orm_registry()
assert isinstance(registry, sqlalchemy_orm.registry)


@map_once
def start_mappers() -> None:
    """
    This method starts the mappers.
    """

    message_table = Table(
        "messages",
        registry.metadata,
        Column("id", String(64), primary_key=True),
        Column("created_time", DateTime),
        Column("updated_time", DateTime),
        Column("message_id", String(64)),
        Column("room_id", String(64)),
        Column("message", Text),
        Column("image", Text),
        Column("username", String(64)),
    )

    registry.map_imperatively(models.Message, message_table)

    setup_model_on_callbacks()

    assert isinstance(component_factory, sqlalchemy_adapter.ComponentFactory)
    registry.metadata.create_all(bind=component_factory.engine)
