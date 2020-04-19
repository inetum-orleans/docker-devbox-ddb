import logging
from typing import Optional, List, Callable, Dict
from typing import TYPE_CHECKING

from dotty_dict import Dotty

if TYPE_CHECKING:
    from ..action import Action  # pylint:disable=cyclic-import


class ContextStackItem:
    """
    A stack item inside context
    """

    def __init__(self, event_name: str, action: 'Action', to_call: Callable, args: list, kwargs: dict):
        self.event_name = event_name
        self.action = action
        self.to_call = to_call
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def _build_parameters_repr(*args, **kwargs):
        parameters_repr = ', '.join(args)
        for key, value in sorted(kwargs.items()):
            if parameters_repr:
                parameters_repr += ', '
            parameters_repr += key + "=" + str(value)
        return parameters_repr

    def __repr__(self):
        parameters_repr = self._build_parameters_repr(*self.args, **self.kwargs)
        return "%s => %s.%s(%s)" % (self.event_name,
                                    type(self.action).__name__,
                                    self.to_call.__name__,
                                    parameters_repr)


class Context:
    """
    Execution context.
    """

    def __init__(self):
        self.phase = None  # type: Optional['Phase']
        self.command = None  # type: Optional['Command']
        self.stack = []  # type: List[ContextStackItem]
        self.exceptions = []  # type: List[Exception]
        self.processed_sources = dict()  # type: Dict[str, str]
        self.processed_targets = dict()  # type: Dict[str, str]
        self.data = Dotty(dict())

    def reset(self):
        """
        Reset the context.
        """
        self.__init__()

    @property
    def event_name(self) -> str:
        """
        Current event name in stack.
        """
        return self.stack[-1].event_name if self.stack else None

    @property
    def action(self) -> 'Action':
        """
        Current action in stack.
        """
        return self.stack[-1].action if self.stack else None

    @property
    def to_call(self) -> Callable:
        """
        Current callable in stack
        """
        return self.stack[-1].to_call if self.stack else None

    @property
    def log(self):
        """
        Logger for current context.
        """
        logger_name = ".".join(["ddb.context"] +
                               list(map(lambda x: x.name,
                                        [x for x in [self.command, self.phase, self.action] if x]))
                               )
        return logging.getLogger(logger_name)

    @property
    def logger(self):
        """
        Logger for current context.
        """
        return self.log

    def mark_as_processed(self, source, target):
        """
        Mark sources and target as processed, for them to be skipped by other file template finders.
        """
        self.processed_sources[source] = target
        self.processed_targets[target] = source

    def mark_as_unprocessed(self, filepath=None):
        """
        Mark sources and target as processed, for them to be skipped by other file template finders.
        """
        if filepath and filepath in self.processed_sources.keys():
            linked_target = self.processed_sources.pop(filepath)
            if linked_target in self.processed_targets.keys():
                self.processed_targets.pop(linked_target)

        if filepath in self.processed_targets:
            linked_source = self.processed_targets.pop(filepath)
            if linked_source in self.processed_sources.keys():
                self.processed_sources.pop(linked_source)
