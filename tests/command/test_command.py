from ddb.command import LifecycleCommand
from ddb.event import bus
from ddb.phase import DefaultPhase, phases


def test_lifecycle():
    phases.register(DefaultPhase("step1"))
    phases.register(DefaultPhase("step2"))

    events = []

    bus.on(None, lambda event, *args, **kwargs: events.append(event))

    command = LifecycleCommand("test", "TestCommand", ["step1", "step2", DefaultPhase("step3")])

    command.execute(good="boy")

    assert events == ["phase:step1", "phase:step2", "phase:step3"]
    events = []

    command.execute()
    assert events == ["phase:step1", "phase:step2", "phase:step3"]
