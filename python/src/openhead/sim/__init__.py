"""Desktop simulator speaking the OpenHead protocol (needs the `[sim]` extra)."""

from .server import SimConfig, SimError, SimServer

__all__ = ["SimConfig", "SimError", "SimServer"]
