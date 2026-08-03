from ..registry import RegistryOrderedSet
from .binary import Binary

__all__ = ["Binary", "binaries"]

binaries: RegistryOrderedSet[Binary] = RegistryOrderedSet(Binary, "Binary")  # type: ignore[type-abstract]
