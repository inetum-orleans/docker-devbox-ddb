from ..registry import RegistryOrderedSet
from .binary import Binary

binaries: RegistryOrderedSet[Binary] = RegistryOrderedSet(Binary, "Binary")  # type: ignore[type-abstract]
