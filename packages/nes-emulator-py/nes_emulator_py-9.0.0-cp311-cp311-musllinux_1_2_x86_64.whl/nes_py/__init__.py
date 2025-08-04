"""The nes-py NES emulator for Python 3."""
from .nes_env import NESEnv


__version__ = "9.0.0"

# explicitly define the outward facing API of this package
__all__ = [NESEnv.__name__]
