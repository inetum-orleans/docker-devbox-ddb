# -*- coding: utf-8 -*-
import inspect
from abc import abstractmethod, ABC
from typing import TypeVar, Generic, Iterable, ClassVar


class RegistryObject(ABC):
    """
    Object that can be registered in a registry. It should have a unique name.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        The name of the object. It should be unique inside the registry.
        """

    @property
    def description(self) -> str:
        """
        The description of the object.
        """
        return inspect.getdoc(self.__class__)


class DefaultRegistryObject(RegistryObject):
    """
    Default object that can be registered in a registry. It should have a unique name.
    """

    def __init__(self, name: str, description: str = None):
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description if self._description else super().description


T = TypeVar('T')  # pylint:disable=invalid-name


class Registry(Generic[T]):
    """
    Container for registered objects. Objects can be retrieved with their unique name.
    """

    def __init__(self, clazz: ClassVar[T], type_name="Object"):
        self._clazz = clazz
        self._type_name = type_name
        self._objects = []
        self._objects_dict = {}

    def _default_name(self, obj: T):  # pylint:disable=no-self-use
        """
        The name getter for an object.
        """
        if hasattr(obj, "name"):
            return obj.name
        raise ValueError("Name should be provided to register this kind of object")

    def register(self, obj: T, name=None):
        """
        Register an object instance.
        """
        name = name if name else self._default_name(obj)

        if not isinstance(obj, self._clazz):
            raise ValueError(self._type_name + " name \"" +
                             name + "\" should be an instance of " +
                             self._clazz.__name__)

        if name in self._objects_dict:
            raise ValueError(self._type_name + " name \"" + name + "\" is already registered")

        self._objects_dict[name] = obj
        self._objects.append(obj)

    def get(self, name: str) -> T:
        """
        Get an object instance from it's unique name.
        """
        if name not in self._objects_dict:
            raise ValueError(self._type_name + " name \"" + name + "\" is not registered")
        return self._objects_dict[name]

    def all(self) -> Iterable[T]:
        """
        Get all object instances.
        """
        return tuple(self._objects)

    def clear(self):
        """
        Remove all object instances.
        """
        self._objects_dict.clear()
        self._objects.clear()
