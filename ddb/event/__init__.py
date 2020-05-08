# -*- coding: utf-8 -*-
from functools import wraps

from .bus import Bus

bus = Bus()


def event(event_name):
    """
    A decorator for event definition
    :param event_name: name of the event
    """

    def decorator(function):
        function.name = event_name

        @wraps(function)
        def perform(*args, **kwargs):
            bus.emit(event_name, *args[1:], **kwargs)

        return perform

    return decorator
