# -*- coding: utf-8 -*-
from .binary import Binary
from ..registry import RegistryOrderedSet

binaries = RegistryOrderedSet(Binary, "Binary")  # type: RegistryOrderedSet[Binary]
