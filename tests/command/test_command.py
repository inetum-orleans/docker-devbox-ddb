from ddb.__main__ import register_default_caches, clear_caches
from ddb.command import LifecycleCommand
from ddb.config import config
from ddb.event import bus
from ddb.phase import DefaultPhase, phases


def test_lifecycle():
    register_default_caches()

    phases.register(DefaultPhase("step1"))
    phases.register(DefaultPhase("step2"))

    config.args.clear_cache = False

    events = []

    bus.on(None, lambda event: events.append(event))

    command = LifecycleCommand("test", "TestCommand", "step1", "step2", DefaultPhase("step3"))

    command.execute()

    assert events == ["phase:step1", "phase:step2", "phase:step3"]
    events = []

    command.execute()
    assert events == ["phase:step1", "phase:step2", "phase:step3"]


def test_lifecycle_run_once():
    register_default_caches()
    clear_caches()

    config.args.clear_cache = False

    phases.register(DefaultPhase("step1", run_once=True))
    phases.register(DefaultPhase("step2"))

    events = []

    bus.on(None, lambda event, *args, **kwargs: events.append(event))

    command = LifecycleCommand("test", "TestCommand", "step1", "step2", "step1", DefaultPhase("step3"))

    command.execute()

    assert events == ["phase:step1", "phase:step2", "phase:step3"]
    events = []

    command.execute()
    assert events == ["phase:step2", "phase:step3"]
