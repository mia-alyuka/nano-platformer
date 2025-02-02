from collections.abc import Callable
from typing import Any
from sdl2 import *
from Scene import Scene
from CommonScreenBuffer import screen_buffer
from useful import load_image_as_texture


class Loading(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.window_size: tuple[int, int] = args[0]
        renderer = args[1]
        self.loading = load_image_as_texture(b"./assets/loading.png", renderer)
        self.has_shown = False
        self.temp_data: Any = None

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        if not self.has_shown:
            self.has_shown = True
            return None
        else:
            data_setter(self.temp_data)
            return "Platformer"

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, self.loading, None, None)
        SDL_RenderPresent(renderer)

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        pass

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_down(self, key: int) -> None:
        pass

    def on_key_up(self, key: int) -> None:
        pass

    def on_enter(self, data: Any) -> None:
        self.temp_data = data
        self.has_shown = False

    def quit(self) -> None:
        SDL_DestroyTexture(self.loading)