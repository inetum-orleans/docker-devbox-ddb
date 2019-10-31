# -*- coding: utf-8 -*-
from .phase import Phase, DefaultPhase
from ..registry import Registry

phases = Registry(Phase, "Phase")
