from collections.abc import Callable
from typing import ClassVar


class Bus:
    """
    Event bus.

    Can be used to register/unregister events listeners, and emit events.
    """

    _named_listeners: ClassVar[dict[str, list[Callable]]] = {}
    _listeners: ClassVar[list[Callable]] = []

    def on(self, event_name: str | None, listener: Callable):
        """
        Register a listener on given event name.
        """
        if event_name:
            if event_name not in self._named_listeners:
                self._named_listeners[event_name] = []
            listeners = self._named_listeners[event_name]
            listeners.append(listener)
        else:
            self._listeners.append(listener)
        return lambda: self.off(event_name, listener)

    def off(self, event_name: str | None, listener: Callable):
        """
        Unregister a listener from given event name.
        """
        if event_name:
            listeners = self._named_listeners.get(event_name)
            if listeners:
                listeners.remove(listener)
        else:
            self._listeners.remove(listener)

    def clear(self):
        """
        Unregister all listeners.
        """
        self._named_listeners.clear()
        self._listeners.clear()

    def emit(self, event_name: str, *args, **kwargs):
        """
        Emit a new event with given payload.
        """
        named_listeners = self._named_listeners.get(event_name)
        if named_listeners:
            for listener in named_listeners:
                listener(*args, **kwargs)

        listeners = self._listeners
        for listener in listeners:
            listener(event_name, *args, **kwargs)

    def has_named_listeners(self, event_name: str) -> bool:
        """
        Check if event_name has at least one named listener registered
        """
        named_listeners = self._named_listeners.get(event_name)
        return bool(named_listeners)
