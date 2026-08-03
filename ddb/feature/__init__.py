from ..registry import Registry
from .feature import Feature

features = Registry(Feature, "Feature")  # type: Registry[Feature]
