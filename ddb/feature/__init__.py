# -*- coding: utf-8 -*-
from .feature import Feature
from ..registry import Registry

features = Registry(Feature, "Feature")  # type: Registry[Feature]
