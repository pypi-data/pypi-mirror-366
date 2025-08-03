"""The kabinet package to interact to the kabinet service."""

from .kabinet import Kabinet

try:
    from .arkitekt import KabinetService
except ImportError:
    pass
try:
    from .rekuest import structure_reg  # type: ignore
except ImportError:
    pass


__all__ = ["Kabinet", "structure_reg", "KabinetService"]
