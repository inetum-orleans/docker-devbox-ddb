from ..registry import Registry
from .service import Service

services = Registry(Service, "Service")  # type: Registry[Service]
