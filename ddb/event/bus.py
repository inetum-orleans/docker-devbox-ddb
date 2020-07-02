# -*- coding: utf-8 -*-
from typing import Callable, Dict, List, Union


class Bus:
    """
    Event bus.

    Can be used to register/unregister events listeners, and emit events.
    """
    _named_listeners = {}  # type: Dict[str, List[Callable]]
    _listeners = []  # type: List[Callable]

    def on(self, event_name: Union[str, None], listener: Callable):  # pylint:disable=invalid-name
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

    def off(self, event_name: Union[str, None], listener: Callable):
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
