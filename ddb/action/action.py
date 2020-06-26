# -*- coding: utf-8 -*-
import os
from abc import abstractmethod, ABC
from typing import Callable, Iterable, Union, Tuple

from ddb.cache import register_project_cache, caches
from ddb.context import context
from ddb.event import events
from ddb.registry import RegistryObject
from ddb.utils.file import write_if_different, TemplateFinder, force_remove


class EventBinding:
    """
    A configured event binding on action.

    event is the event name

    call is a callable that will be invoked with event *args, **kwargs.

    processor is used to process the event before invoking the callable.
    If processor returns False, callable will not be invoked.
    If processor returns a 2-tuple, it will use those as *args, **kwargs to invoke the method.
    """

    def __init__(self, event: Union[Callable, str], call: Callable = None, processor: Callable = None):
        self.event = event
        self.call = call
        self.processor = processor


class Action(RegistryObject, ABC):
    """
    Action can perform something on the system through "execute" method, or any other.
    """

    @property
    @abstractmethod
    def event_bindings(self) -> Union[Iterable[Union[Callable, str, EventBinding]], Union[Callable, str, EventBinding]]:
        """
        The event bindings that should trigger the action.

        A binding can be defined as a string matching the event name and will register the "execute" method on event
        bus.

        A binding can also be defined as EventBinding instance.
        """

    @property
    def order(self) -> int:
        """
        The order index related to this action.

        When many actions are registered on the same event name, they will be executed in sequence following the
        natural ordering from this value.
        """
        return 0

    @property
    def disabled(self) -> bool:
        """
        Check if the action is disabled.
        """
        return False


class InitializableAction(Action, ABC):  # pylint:disable=abstract-method
    """
    An action supporting an initialize singleton method.
    """

    def __init__(self):
        self.initialized = False

    def initialize(self):
        """
        Initialize method, invoked before first event binding execution.
        """


class WatchSupport(ABC):
    """
    Watch support
    """

    @abstractmethod
    def start_watching(self):
        """
        Start watching
        """

    @abstractmethod
    def stop_watching(self):
        """
        Stop watching
        """

    @abstractmethod
    def join_watching(self):
        """
        Join watching
        """


class AbstractTemplateAction(InitializableAction, ABC):  # pylint:disable=abstract-method
    """
    Abstract action to render templates based on filename suffixes, supporting incoming events from file feature.
    """

    def __init__(self):
        super().__init__()
        self.template_finder = None  # type: TemplateFinder
        register_project_cache(self._cache_key)

    @property
    def _cache_key(self):
        """
        This cache is used to store the rendered data of all targets.
        When a template is deleted, target file will remove only if content is still the same than the generated one,
        thanks to this cache.
        """
        return "template.target." + self.__class__.__name__

    @property
    def event_bindings(self):
        def file_found_processor(file: str):
            template = file
            target = self.template_finder.get_target(template)
            if target:
                return (), {"template": template, "target": target}
            return None

        def file_delete_processor(file: str):
            template = file
            target = self.template_finder.get_target(template)
            if target and not self._target_is_modified(template, target):
                return (), {"template": template, "target": target}
            return None

        def file_generated_processor(source: str, target: str):
            template = target
            target = self.template_finder.get_target(template)
            if target:
                return (), {"template": template, "target": target}
            return None

        return (EventBinding(events.file.found, processor=file_found_processor),
                EventBinding(events.file.deleted, call=self.delete, processor=file_delete_processor),
                EventBinding("file:generated", processor=file_generated_processor))

    def initialize(self):
        self.template_finder = self._build_template_finder()

    def delete(self, template: str, target: str):
        """
        Delete a rendered template
        """
        if os.path.exists(target):
            force_remove(target)
            context.log.warning("%s removed", target)
            caches.get(self._cache_key).pop(target)
            events.file.deleted(target)

    def execute(self, template: str, target: str):
        """
        Render a template
        """
        for rendered, destination in self._render_template(template, target):
            written = False
            if not isinstance(rendered, bool):
                is_bynary = isinstance(rendered, (bytes, bytearray))
                written = write_if_different(destination, rendered,
                                             'rb' if is_bynary else 'r',
                                             'wb' if is_bynary else 'w',
                                             log_source=template)
                caches.get(self._cache_key).set(target, rendered)
            context.mark_as_processed(template, destination)

            if written or rendered is True:
                events.file.generated(source=template, target=destination)

    def _target_is_modified(self, template: str, target: str) -> bool:
        rendered = caches.get(self._cache_key).get(target)
        if rendered is None:
            return True
        if not os.path.exists(target):
            caches.get(self._cache_key).pop(target)
            return True
        is_bynary = isinstance(rendered, (bytes, bytearray))
        read_encoding = None if is_bynary else "utf-8"
        with open(target, mode='rb' if is_bynary else 'r', encoding=read_encoding) as read_file:
            existing_data = read_file.read()
        return existing_data != rendered

    @abstractmethod
    def _build_template_finder(self) -> TemplateFinder:
        """
        Build the template finder.
        """

    @abstractmethod
    def _render_template(self, template: str, target: str) -> Iterable[Tuple[Union[str, bytes, bool], str]]:
        """
        Perform template rendering to a string.
        """
