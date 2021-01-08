# -*- coding: utf-8 -*-
import inspect
from abc import abstractmethod, ABC
from collections import defaultdict
from typing import TypeVar, Generic, ClassVar, TYPE_CHECKING, Tuple, Optional, Callable, Any

from ordered_set import OrderedSet

if TYPE_CHECKING:
    from ddb.cache import Cache  # pylint:disable=cyclic-import


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
        self._cache = None

    def set_cache(self, cache: 'Cache'):
        """
        Set a cache provider, and register cached entries into registry.
        """
        self._cache = cache
        if self._cache:
            for key in self._cache.keys():
                self._register_cache_value_impl(self._cache.get(key), key)

    def _register_cache_value_impl(self, value, key):
        self.register(value, key)

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

        data = self._register_impl(name, obj)
        return data

    def _register_impl(self, name: str, obj: T):
        if name in self._objects_dict:
            raise ValueError(self._type_name + " name \"" + name + "\" is already registered")

        self._objects_dict[name] = obj
        self._objects.append(obj)

        if self._cache and obj and (name not in self._cache or self._cache.get(name) != obj):
            self._cache.set(name, obj)
            self._cache.flush()

        return obj

    def has(self, name: str, obj: Optional[T] = None) -> bool:
        """
        Check if name is registered.
        """
        ret = name in self._objects_dict
        if ret and obj is not None:
            return self._has_obj_impl(self._objects_dict.get(name), obj)
        return ret

    def _has_obj_impl(self, dict_value, obj) -> bool:  # pylint:disable=no-self-use
        return dict_value == obj

    def unregister(self, name, obj: Optional[T] = None, callback: Optional[Callable[[T], Any]] = None) -> bool:
        """
        Unregister an object instance
        """
        if name not in self._objects_dict:
            raise ValueError(self._type_name + " name \"" + name + "\" is not registered")

        return self._unregister_impl(name, obj, callback)

    def _unregister_impl(self, name, obj=None, callback: Optional[Callable[[T], Any]] = None) -> bool:
        item = self._objects_dict.get(name)
        if obj is None or item == obj:
            self._objects_dict.pop(name)
            self._objects.remove(item)

            if self._cache and name in self._cache:
                self._cache.pop(name)

            if callback:
                callback(item)

            return True
        return False

    def get(self, name: str) -> T:
        """
        Get an object instance from it's unique name.
        """
        if name not in self._objects_dict:
            raise ValueError(self._type_name + " name \"" + name + "\" is not registered")
        return self._objects_dict[name]

    def all(self) -> Tuple[T]:
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
        if self._cache:
            self._cache.clear()

    def close(self):
        """
        Close this registry, closing the underlying cache if defined and then removing all objects instances.
        :return:
        """
        if self._cache:
            self._cache.close()
            self._cache = None
        self.clear()


class RegistryOrderedSet(Registry):
    """
    Container for registered objects. Objects set can be retrieved with their unique name.
    """
    def __init__(self, clazz: ClassVar[T], type_name="Object"):
        super().__init__(clazz, type_name)
        self._objects_dict = defaultdict(OrderedSet)

    def _register_cache_value_impl(self, value, key):
        for obj in value:
            self.register(obj, key)

    def _register_impl(self, name: str, obj: T):
        items = self._objects_dict[name]
        if obj in items:
            raise ValueError("This " + self._type_name + " is already registered for name \"" + name + "\"")
        items.add(obj)
        self._objects.append(obj)

        if self._cache:
            self._cache.set(name, items)
            self._cache.flush()

        return items

    def _unregister_impl(self, name, obj=None, callback: Optional[Callable[[T], Any]] = None) -> bool:
        items = self._objects_dict.get(name)
        ret = False
        if items:
            for item in items:
                if not obj or obj == item:
                    items.remove(item)
                    self._objects.remove(item)
                    ret = True
                    if callback:
                        callback(item)
            if ret:
                if not items:
                    self._objects_dict.pop(name)
                    if self._cache and name in self._cache:
                        self._cache.pop(name)
                else:
                    if self._cache:
                        self._cache.set(name, items)
        return ret

    def _has_obj_impl(self, dict_value: OrderedSet[T], obj) -> bool:
        return obj in dict_value

    def get(self, name: str) -> OrderedSet[T]:  # pylint:disable=useless-super-delegation
        return super().get(name)
