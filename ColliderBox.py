from dataclasses import dataclass
from typing import Self


@dataclass
class ColliderBox:
    x: float
    y: float
    width: float
    height: float
    deadly: bool = False

    def is_colliding(self, another: Self) -> bool:
        horizontal = self.x < another.x + another.width and self.x + self.width > another.x
        vertical = self.y < another.y + another.height and self.y + self.height > another.y
        return horizontal and vertical
