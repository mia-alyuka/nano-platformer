from abc import ABC
from dataclasses import dataclass
from ColliderBox import ColliderBox


class SpecialObject(ABC):
    pass


@dataclass
class RespawnPoint(SpecialObject):
    position: tuple[int, int]


@dataclass
class JumpPad(SpecialObject):
    position: tuple[int, int]
    collider: ColliderBox


@dataclass
class JumpOrb(SpecialObject):
    position: tuple[int, int]
    collider: ColliderBox
    inactive_timer: float = 0.0


@dataclass
class DashOrb(SpecialObject):
    position: tuple[int, int]
    collider: ColliderBox
    inactive_timer: float = 0.0


@dataclass
class RoomFinish(SpecialObject):
    collider: ColliderBox


@dataclass
class Checkpoint(SpecialObject):
    position: tuple[int, int]
    collider: ColliderBox
    active: bool = False
