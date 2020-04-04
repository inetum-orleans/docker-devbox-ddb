import logging
from typing import Optional, Union
from typing import TYPE_CHECKING

import colorlog
from dotty_dict import Dotty

if TYPE_CHECKING:
    from ..action import Action  # pylint:disable=cyclic-import
    from ..phase import Phase  # pylint:disable=cyclic-import
    from ..command import Command  # pylint:disable=cyclic-import


class Context:
    """
    Execution context.
    """

    def __init__(self):
        self.phase = None  # type: Optional[Phase]
        self.action = None  # type: Optional[Action]
        self.command = None  # type: Optional[Command]
        self.processed_sources = set()
        self.processed_targets = set()
        self.data = Dotty(dict())

    def reset(self):
        """
        Reset the context.
        """
        self.__init__()

    @property
    def log(self):
        """
        Logger for current context.
        """
        logger_name = ".".join(["context"] +
                               list(map(lambda x: x.name, [x for x in [self.command, self.phase, self.action] if x]))
                               )
        return logging.getLogger(logger_name)

    @property
    def logger(self):
        """
        Logger for current context.
        """
        return self.log


class CustomFormatter(colorlog.ColoredFormatter):
    """
    Custom context logger formatter.
    """

    def format(self, record):
        record.simplename = record.name.rsplit(".", 1)[-1]
        return super().format(record)


def configure_context_logger(level: Union[str, int] = logging.INFO):
    """
    Configure context logger.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter('%(log_color)s[%(simplename)s] %(message)s'))

    logger = logging.getLogger('context')
    logger.setLevel(level)
    logger.addHandler(handler)
