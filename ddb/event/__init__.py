from collections.abc import Callable
from functools import wraps
from typing import ParamSpec

from .bus import Bus

__all__ = ["Bus", "bus", "event", "event_name"]

bus = Bus()

P = ParamSpec("P")


def event(event_name: str) -> Callable[[Callable[P, None]], Callable[P, None]]:
    """
    A decorator for event definition.

    :param event_name: name of the event.
    """

    def decorator(function: Callable[P, None]) -> Callable[P, None]:
        function.name = event_name  # type: ignore[attr-defined]

        @wraps(function)
        def perform(*args: P.args, **kwargs: P.kwargs) -> None:
            bus.emit(event_name, *args[1:], **kwargs)

        return perform

    return decorator


def event_name(declaration: Callable[..., None]) -> str:
    """
    Get the event name carried by a callable declared with the @event decorator.
    """
    return str(declaration.name)  # type: ignore[attr-defined]
