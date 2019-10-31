# -*- coding: utf-8 -*-
from .binary import Binary
from ..registry import Registry

binaries = Registry(Binary, "Binary")  # type: Registry[Binary]
