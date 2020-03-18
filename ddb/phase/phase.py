# -*- coding: utf-8 -*-
from abc import ABC
from argparse import ArgumentParser
from typing import Any, Callable, Union

from ddb.cache import project_cache
from ddb.context import context
from ddb.event import bus
from ddb.registry import RegistryObject, DefaultRegistryObject


class Phase(RegistryObject, ABC):  # pylint:disable=abstract-method
    """
    Step into a lifecycle flow.
    """

    def configure_parser(self, parser: ArgumentParser):
        """
        Configure the argument parser.
        """

    def execute(self, *args, **kwargs):
        """
        Execute the phase.
        """


class DefaultPhase(DefaultRegistryObject, Phase):
    """
    Default implementation for a phase.
    """

    def __init__(self,
                 name: str,
                 description: Union[str, None] = None,
                 parser: Callable[[ArgumentParser], Any] = None,
                 run_once: bool = False):
        super().__init__(name, description)
        self.run_once = run_once
        self._parser = parser

    def configure_parser(self, parser: ArgumentParser):
        if self._parser:
            self._parser(parser)

    def execute(self, *args, **kwargs):
        cache = project_cache()
        runned_cache_key = "phase.runned." + self.name
        if self.run_once and cache.get(runned_cache_key):
            return
        bus.emit("phase:" + self.name, *args, **kwargs)
        cache.set(runned_cache_key, True)
        cache.flush()


def execute_phase(phase: Phase, *args, **kwargs):
    """
    Execute a phase with context update.
    """
    context.phase = phase
    try:
        phase.execute(*args, **kwargs)
    finally:
        context.phase = None
