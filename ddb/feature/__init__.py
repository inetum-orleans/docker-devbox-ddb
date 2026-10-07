from ..registry import Registry
from .feature import Feature

__all__ = ["Feature", "features"]

features: Registry[Feature] = Registry(Feature, "Feature")  # type: ignore[type-abstract]
