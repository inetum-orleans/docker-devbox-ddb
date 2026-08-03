from ..registry import RegistryOrderedSet
from .binary import Binary

binaries = RegistryOrderedSet(Binary, "Binary")  # type: RegistryOrderedSet[Binary]
