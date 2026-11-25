"""The controller interface.

A motion controller turns "where the agent is" and "how fast it is allowed to go" into a
control ``(v, omega)``. Conflict resolution reaches it only through ``speed_bound``, which
is how the paper describes it too: "We enforce the follower's slowdown by changing the
upper bound of the linear velocity constraint" (arXiv:2503.12333v1, Sec IV-B). Any backend
that honours that bound can be swapped in without touching the rest of the simulator.

Backends register themselves by name with :func:`register_controller`; a scenario picks
one with ``controller: {backend: <name>, ...}``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable

from ..core.agent import AgentRuntime
from ..core.state import Control
from ..core.world import World


class MotionController(ABC):
    name: str

    @abstractmethod
    def compute(self, agent: AgentRuntime, speed_bound: float, world: World) -> Control:
        """Control for ``agent`` this step, with linear velocity at most ``speed_bound``."""


_REGISTRY: dict[str, Callable[..., MotionController]] = {}


def register_controller(name: str) -> Callable[[type], type]:
    def decorator(cls: type) -> type:
        if name in _REGISTRY:
            raise ValueError(f"controller backend {name!r} is already registered")
        cls.name = name
        _REGISTRY[name] = cls
        return cls

    return decorator


def available_controllers() -> list[str]:
    return sorted(_REGISTRY)


def make_controller(backend: str, **params) -> MotionController:
    if backend not in _REGISTRY:
        hint = ""
        if backend == "mpc_cbf":
            hint = (
                " The MPC-CBF backend of the paper is not implemented; see "
                "docs/architecture.md, 'Controller backends'."
            )
        raise ValueError(
            f"unknown controller backend {backend!r}; available: {available_controllers()}.{hint}"
        )
    return _REGISTRY[backend](**params)
