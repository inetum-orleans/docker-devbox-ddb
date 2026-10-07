import logging
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, Any

import verboselogs
from dotty_dict import Dotty

if TYPE_CHECKING:
    from ..action import Action
    from ..command import Command
    from ..phase import Phase


class ContextStackItem:
    """
    A stack item inside context.
    """

    def __init__(
        self,
        event_name: str,
        action: "Action",
        to_call: Callable[..., Any],
        args: Sequence[Any],
        kwargs: dict[str, Any],
    ) -> None:
        self.event_name = event_name
        self.action = action
        self.to_call = to_call
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def _build_parameters_repr(*args: Any, **kwargs: Any) -> str:
        parameters_repr = ", ".join(map(str, args))
        for key, value in sorted(kwargs.items()):
            if parameters_repr:
                parameters_repr += ", "
            parameters_repr += key + "=" + str(value)
        return parameters_repr

    def __repr__(self) -> str:
        parameters_repr = self._build_parameters_repr(*self.args, **self.kwargs)
        return f"{self.event_name} => {type(self.action).__name__}.{self.to_call.__name__}({parameters_repr})"


class Context:
    """
    Execution context.
    """

    def __init__(self) -> None:
        self.phase: Phase | None = None
        self.command: Command | None = None
        self.stack: list[ContextStackItem] = []
        self.watching = False
        self.exceptions: list[Exception] = []
        self.processed_sources: dict[str, str] = {}
        self.processed_targets: dict[str, str] = {}
        self.data = Dotty({})

    def reset(self) -> None:
        """
        Reset the context.
        """
        Context.__init__(self)

    @property
    def event_name(self) -> str | None:
        """
        Current event name in stack.
        """
        return self.stack[-1].event_name if self.stack else None

    @property
    def action(self) -> "Action | None":
        """
        Current action in stack.
        """
        return self.stack[-1].action if self.stack else None

    @property
    def to_call(self) -> Callable[..., Any] | None:
        """
        Current callable in stack.
        """
        return self.stack[-1].to_call if self.stack else None

    @property
    def log(self) -> verboselogs.VerboseLogger:
        """
        Logger for current context.
        """
        stack_items = [item for item in (self.command, self.phase, self.action) if item]
        logger_name = ".".join(["ddb.context", *[item.name for item in stack_items]])
        return logging.getLogger(logger_name)

    @property
    def logger(self) -> verboselogs.VerboseLogger:
        """
        Logger for current context.
        """
        return self.log

    def mark_as_processed(self, source: str, target: str) -> None:
        """
        Mark sources and target as processed, for them to be skipped by other file template finders.
        """
        self.processed_sources[source] = target
        self.processed_targets[target] = source

    def mark_as_unprocessed(self, filepath: str | None = None) -> None:
        """
        Mark sources and target as processed, for them to be skipped by other file template finders.
        """
        if filepath and filepath in self.processed_sources:
            linked_target = self.processed_sources.pop(filepath)
            if linked_target in self.processed_targets:
                self.processed_targets.pop(linked_target)

        if filepath in self.processed_targets:
            linked_source = self.processed_targets.pop(filepath)
            if linked_source in self.processed_sources:
                self.processed_sources.pop(linked_source)
