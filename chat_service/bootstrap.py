"""
This module contains the bootstrap function for the allocation application.
"""

import os

import core
import utils
from core.dependency_injection import inject_dependencies
from chat_service.adapters.orm import start_mappers
from chat_service.services import command, event

config = utils.get_config()


def bootstrap(
    start_orm: bool = True,
) -> core.MessageBus:
    """
    Bootstrap the allocation application.

    Args:
        start_orm: A boolean indicating whether to start the ORM.
        uow: An instance of the unit of work.

    Returns:
        An instance of the MessageBus.
    """
    if start_orm:
        start_mappers()

    uow = core.UnitOfWork(config["database"])

    dependencies = {
        "uow": uow,
    }
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ]
        for event_type, event_handlers in event.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in command.COMMAND_HANDLERS.items()
    }

    return core.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )
