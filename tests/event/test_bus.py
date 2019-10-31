# -*- coding: utf-8 -*-

from ddb.event import Bus


def test_with_event_name():
    bus = Bus()

    custom_event_listeners = []

    def listener(data):
        custom_event_listeners.append(data)

    bus.on("custom:event", listener)
    bus.emit("custom:event", "testing")
    bus.emit("custom:event2", "another")

    bus.off("custom:event", listener)
    bus.emit("custom:event", "more")

    assert custom_event_listeners == ["testing"]


def test_without_event_name():
    bus = Bus()

    custom_event_listeners = []

    def listener(event, data):
        custom_event_listeners.append((event, data))

    bus.on(None, listener)
    bus.emit("custom:event", "testing")
    bus.emit("custom:event2", "another")

    bus.off(None, listener)
    bus.emit("custom:event", "more")

    assert custom_event_listeners == [("custom:event", "testing"), ("custom:event2", "another")]
