from ..registry import Registry
from .feature import Feature

features: Registry[Feature] = Registry(Feature, "Feature")  # type: ignore[type-abstract]
