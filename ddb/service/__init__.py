from ..registry import Registry
from .service import Service

__all__ = ["Service", "services"]

services: Registry[Service] = Registry(Service, "Service")  # type: ignore[type-abstract]
