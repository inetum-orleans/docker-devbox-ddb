# -*- coding: utf-8 -*-
import pytest

from ddb.binary.binary import DefaultBinary, Binary
from ddb.feature.docker.binaries import DockerBinary
from ddb.registry import Registry, DefaultRegistryObject, RegistryOrderedSet


class Dummy(DefaultRegistryObject):
    pass


class Another(DefaultRegistryObject):
    pass


class HashbableDummy(DefaultRegistryObject):
    def __init__(self, name, a, b):
        super().__init__(name)
        self.a = a
        self.b = b

    def __eq__(self, other):
        if not isinstance(other, HashbableDummy):
            return False
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        return hash(self.a) ^ hash(self.b)


class NoName:
    pass


class TestRegistry:
    def test_empty(self):
        r = Registry(Dummy, "Dummy")

        assert r.all() == ()

    def test_register(self):
        r = Registry(Dummy, "Dummy")

        d = Dummy("dummy")
        r.register(d)

        assert r.get("dummy") == d
        assert r.all() == (d,)

    def test_register_and_unregister(self):
        r = Registry(Dummy, "Dummy")

        d = Dummy("dummy")
        r.register(d)

        assert r.get("dummy") == d
        assert r.all() == (d,)

        r.unregister("dummy")
        with pytest.raises(ValueError) as e:
            r.get("dummy")
        assert str(e.value) == "Dummy name \"dummy\" is not registered"
        assert not r.has("dummy")
        assert r.all() == ()

    def test_register_alternative_name(self):
        r = Registry(Dummy, "Dummy")

        d = Dummy("dummy")
        r.register(d, "alt")

        with pytest.raises(ValueError) as e:
            r.get("dummy")
        assert str(e.value) == "Dummy name \"dummy\" is not registered"

        assert r.get("alt") == d
        assert r.all() == (d,)

    def test_cant_register_many_times(self):
        r = Registry(Dummy, "Dummy")

        d = Dummy("dummy")
        r.register(d)

        with pytest.raises(ValueError) as e:
            r.register(d)
        assert str(e.value) == "Dummy name \"dummy\" is already registered"

    def test_unregistered(self):
        r = Registry(Dummy, "Dummy")

        with pytest.raises(ValueError) as e:
            r.get("dummy")
        assert str(e.value) == "Dummy name \"dummy\" is not registered"

    def test_register_another_class(self):
        r = Registry(Dummy, "Dummy")

        with pytest.raises(ValueError) as e:
            r.register(Another("testing"))
        assert str(e.value) == "Dummy name \"testing\" should be an instance of Dummy"

    def test_register_invalid_instance(self):
        r = Registry(Dummy, "Dummy")

        n = NoName()

        with pytest.raises(ValueError) as e:
            r.register(n, "no-name")
        assert str(e.value) == "Dummy name \"no-name\" should be an instance of Dummy"

    def test_register_no_name_class_missing_name(self):
        r = Registry(NoName, "NoName")

        n = NoName()

        with pytest.raises(ValueError) as e:
            r.register(n)
        assert str(e.value) == "Name should be provided to register this kind of object"


class TestRegistrySet:
    def test_empty(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        assert len(r.all()) == 0

    def test_register(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        d = HashbableDummy("dummy", "1", "2")
        r.register(d)

        assert r.get("dummy") == [d]

    def test_register_and_unregister(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        d = HashbableDummy("dummy", "1", "2")
        r.register(d)

        assert r.get("dummy") == {d}
        assert r.all() == (d,)

        r.unregister("dummy")
        with pytest.raises(ValueError) as e:
            r.get("dummy")
        assert str(e.value) == "HashbableDummy name \"dummy\" is not registered"
        assert not r.has("dummy")
        assert r.all() == ()

    def test_register_alternative_name(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        d = HashbableDummy("dummy", "1", "2")
        r.register(d, "alt")

        with pytest.raises(ValueError) as e:
            r.get("dummy")
        assert str(e.value) == "HashbableDummy name \"dummy\" is not registered"

        assert r.get("alt") == {d}

    def test_skip_allready_registered_same_instance(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        d = HashbableDummy("dummy", "1", "2")
        r.register(d)

        d2 = HashbableDummy("dummy", "1", "2")
        with pytest.raises(ValueError) as e:
            r.register(d2)
        assert str(e.value) == "This HashbableDummy is already registered for name \"dummy\""

        d3 = HashbableDummy("dummy", "1", "3")
        r.register(d3)

        assert r.get("dummy") == {d, d3}
        assert r.all() == (d, d3)

    def test_unregistered(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        with pytest.raises(ValueError) as e:
            r.get("dummy")
        assert str(e.value) == "HashbableDummy name \"dummy\" is not registered"

    def test_register_another_class(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        with pytest.raises(ValueError) as e:
            r.register(Another("testing"))
        assert str(e.value) == "HashbableDummy name \"testing\" should be an instance of HashbableDummy"

    def test_register_invalid_instance(self):
        r = RegistryOrderedSet(HashbableDummy, "HashbableDummy")

        n = NoName()

        with pytest.raises(ValueError) as e:
            r.register(n, "no-name")
        assert str(e.value) == "HashbableDummy name \"no-name\" should be an instance of HashbableDummy"

    def test_register_no_name_class_missing_name(self):
        r = RegistryOrderedSet(NoName, "NoName")

        n = NoName()

        with pytest.raises(ValueError) as e:
            r.register(n)
        assert str(e.value) == "Name should be provided to register this kind of object"

    def test_binary_ordering(self):
        binary1 = DockerBinary("npm", "node1")
        binary2 = DockerBinary("npm", "node2")
        default_binary = DefaultBinary("npm", ["npm"])
        binary4 = DockerBinary("npm", "node4")
        binary_with_condition = DockerBinary("npm", "node5", condition="some-condition")

        bins = (binary1, binary2, default_binary, binary4, binary_with_condition)

        r = RegistryOrderedSet(Binary, "Binary")
        for bin in bins:
            r.register(bin)

        assert r.all() == bins
        npm_binaries = r.get("npm")

        assert npm_binaries == bins
