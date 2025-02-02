from collections.abc import Callable
from ctypes import byref
from typing import Any
from sdl2 import *
from Button import Button
from Scene import Scene
from CommonScreenBuffer import screen_buffer
from useful import load_image_as_texture


class MainMenu(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.window_size: tuple[int, int] = args[0]
        renderer = args[1]
        self.cool_title = load_image_as_texture(b"./assets/title.png", renderer)
        self.start_button = Button(renderer, "start", (-1, 500), self.window_size)
        self.settings_button = Button(renderer, "settings", (-1, 560), self.window_size)
        self.credits_button = Button(renderer, "credits", (-1, 620), self.window_size)
        self.exit_button = Button(renderer, "exit", (-1, 680), self.window_size)
        self.should_go_next: str | None = None

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        self.exit_button.update()
        self.credits_button.update()
        self.start_button.update()
        self.settings_button.update()
        if self.should_go_next is not None:
            tmp = self.should_go_next
            self.should_go_next = None
            return tmp
        return None

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, screen_buffer())
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
        SDL_RenderClear(renderer)
        self.exit_button.draw(renderer)
        self.credits_button.draw(renderer)
        self.start_button.draw(renderer)
        self.settings_button.draw(renderer)
        dst = SDL_Rect(672, 100, 576, 324)
        SDL_RenderCopy(renderer, self.cool_title, None, byref(dst))
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, screen_buffer(), None, None)
        SDL_RenderPresent(renderer)

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        if self.exit_button.hovering:
            self.should_go_next = "SceneManager Quit"
        elif self.credits_button.hovering:
            self.should_go_next = "Credits"
        elif self.settings_button.hovering:
            pass
        elif self.start_button.hovering:
            self.should_go_next = "Map selector"

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_down(self, key: int) -> None:
        pass

    def on_key_up(self, key: int) -> None:
        pass

    def on_enter(self, data: Any) -> None:
        pass

    def quit(self) -> None:
        SDL_DestroyTexture(self.cool_title)
        self.start_button.destroy()
        self.settings_button.destroy()
        self.credits_button.destroy()
        self.exit_button.destroy()
