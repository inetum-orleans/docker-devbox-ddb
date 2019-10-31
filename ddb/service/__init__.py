# -*- coding: utf-8 -*-
from .service import Service
from ..registry import Registry

services = Registry(Service, "Service")  # type: Registry[Service]
