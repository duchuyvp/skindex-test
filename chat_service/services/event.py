from typing import Callable, Any
import core

EVENT_HANDLERS: dict[type[core.Event], list[Callable[..., None]]] = {}
