# -*- coding: utf-8 -*-
from abc import ABC

from ddb.registry import RegistryObject


class Service(RegistryObject, ABC):  # pylint:disable=abstract-method
    """
    Service
    """
