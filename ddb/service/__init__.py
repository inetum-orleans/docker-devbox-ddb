from ..registry import Registry
from .service import Service

services: Registry[Service] = Registry(Service, "Service")  # type: ignore[type-abstract]
