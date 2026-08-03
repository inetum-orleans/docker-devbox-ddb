from ..registry import Registry
from .phase import DefaultPhase, Phase

__all__ = ["DefaultPhase", "Phase", "phases"]

phases = Registry(Phase, "Phase")
