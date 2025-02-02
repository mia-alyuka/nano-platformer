from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any
from sdl2 import *


class Scene(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        pass

    @abstractmethod
    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        pass

    @abstractmethod
    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        pass

    @abstractmethod
    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    @abstractmethod
    def on_key_down(self, key: int) -> None:
        pass

    @abstractmethod
    def on_key_up(self, key: int) -> None:
        pass

    @abstractmethod
    def on_enter(self, data: Any) -> None:
        pass

    @abstractmethod
    def quit(self) -> None:
        pass
