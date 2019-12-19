# -*- coding: utf-8 -*-
import pytest

from ddb.registry import Registry, DefaultRegistryObject


class Dummy(DefaultRegistryObject):
    pass


class Another(DefaultRegistryObject):
    pass


class NoName:
    pass


def test_empty():
    r = Registry(Dummy, "Dummy")

    assert len(r.all()) == 0


def test_register():
    r = Registry(Dummy, "Dummy")

    d = Dummy("dummy")
    r.register(d)

    assert r.get("dummy") == d


def test_register_alternative_name():
    r = Registry(Dummy, "Dummy")

    d = Dummy("dummy")
    r.register(d, "alt")

    with pytest.raises(ValueError) as e:
        r.get("dummy")
    assert str(e.value) == "Dummy name \"dummy\" is not registered"

    assert r.get("alt") == d


def test_cant_register_many_times():
    r = Registry(Dummy, "Dummy")

    d = Dummy("dummy")
    r.register(d)

    with pytest.raises(ValueError) as e:
        r.register(d)
    assert str(e.value) == "Dummy name \"dummy\" is already registered"


def test_unregistered():
    r = Registry(Dummy, "Dummy")

    with pytest.raises(ValueError) as e:
        r.get("dummy")
    assert str(e.value) == "Dummy name \"dummy\" is not registered"


def test_register_another_class():
    r = Registry(Dummy, "Dummy")

    with pytest.raises(ValueError) as e:
        r.register(Another("testing"))
    assert str(e.value) == "Dummy name \"testing\" should be an instance of Dummy"


def test_register_invalid_instance():
    r = Registry(Dummy, "Dummy")

    n = NoName()

    with pytest.raises(ValueError) as e:
        r.register(n, "no-name")
    assert str(e.value) == "Dummy name \"no-name\" should be an instance of Dummy"


def test_register_no_name_class_missing_name():
    r = Registry(NoName, "NoName")

    n = NoName()

    with pytest.raises(ValueError) as e:
        r.register(n)
    assert str(e.value) == "Name should be provided to register this kind of object"
