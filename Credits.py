from collections.abc import Callable
from typing import Any
from sdl2 import *
from Scene import Scene
from Button import Button
from CommonScreenBuffer import screen_buffer
from useful import load_image_as_texture


class Credits(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.window_size: tuple[int, int] = args[0]
        renderer = args[1]
        self.the_credits = load_image_as_texture(b"./assets/credits.png", renderer)
        self.back_button = Button(renderer, "back", (-1, 1000), self.window_size)
        self.should_quit = False

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        self.back_button.update()
        if self.should_quit:
            self.should_quit = False
            return "Main menu"
        return None

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, screen_buffer())
        SDL_RenderCopy(renderer, self.the_credits, None, None)
        self.back_button.draw(renderer)
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, screen_buffer(), None, None)
        SDL_RenderPresent(renderer)

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        if self.back_button.hovering:
            self.should_quit = True

    def on_key_down(self, key: int) -> None:
        pass

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_up(self, key: int) -> None:
        pass

    def on_enter(self, data: Any) -> None:
        pass

    def quit(self) -> None:
        SDL_DestroyTexture(self.the_credits)
        self.back_button.destroy()
