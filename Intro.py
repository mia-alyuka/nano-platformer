from collections.abc import Callable
from time import time
from typing import Any
from sdl2 import *
from Scene import Scene
from useful import load_image_as_texture


def magic_function(x: float) -> float:
    return -4/25*x*(x-5)


class Intro(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.start_time = time()
        self.window_size: tuple[int, int] = args[0]
        renderer = args[1]
        self.intro_image = load_image_as_texture(b"./assets/intro.png", renderer)
        self.skip = False
        self.magic_value = 0.0

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        delta = time() - self.start_time
        if delta > 5 or self.skip:
            return "Main menu"
        self.magic_value = magic_function(delta)
        return None

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, None)
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
        SDL_RenderClear(renderer)
        alpha = min(255, int(self.magic_value * 255))
        SDL_SetTextureAlphaMod(self.intro_image, alpha)
        SDL_RenderCopy(renderer, self.intro_image, None, None)
        SDL_RenderPresent(renderer)

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        pass

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_down(self, key: int) -> None:
        if key == SDLK_j:
            self.skip = True

    def on_key_up(self, key: int) -> None:
        pass

    def on_enter(self, data: Any) -> None:
        pass

    def quit(self) -> None:
        SDL_DestroyTexture(self.intro_image)
