from collections.abc import Callable
from ctypes import c_int, byref
from typing import Any
from sdl2 import *
from sdl2.sdlttf import *
from sdl2.sdlgfx import *
from Button import Button
from CommonScreenBuffer import screen_buffer
from Scene import Scene
from useful import load_image_as_texture, render_utf8_solid_as_texture

WHITE = SDL_Color(255, 255, 255, SDL_ALPHA_OPAQUE)

class MapCompleted(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.window_size: tuple[int, int] = args[0]
        renderer = args[1]
        self.renderer = args[1]
        self.completed_img = load_image_as_texture(b"./assets/completed.png", renderer)
        self.font = TTF_OpenFont(b"./assets/TinyUnicode.ttf", 64)
        self.map_completed_img: SDL_Texture | None = None
        self.respawns: SDL_Texture | None = None
        self.time_elapsed_img: SDL_Texture | None = None
        self.player_deaths = 0
        self.time_elapsed = 0.0
        self.map_completed = ""
        self.fade_timer = 1.0
        self.back_button = Button(renderer, "back", (-1, 700), self.window_size)
        self.go_back = False

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        self.back_button.update()
        self.fade_timer -= delta_time
        if self.go_back:
            self.go_back = False
            self.fade_timer = 1.0
            return "Main menu"
        return None

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, screen_buffer())
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
        SDL_RenderClear(renderer)
        w1, h1 = c_int(0), c_int(0)
        w2, h2 = c_int(0), c_int(0)
        w3, h3 = c_int(0), c_int(0)
        w4, h4 = c_int(0), c_int(0)
        SDL_QueryTexture(self.completed_img, None, None, byref(w1), byref(h1))
        SDL_QueryTexture(self.map_completed_img, None, None, byref(w2), byref(h2))
        SDL_QueryTexture(self.respawns, None, None, byref(w3), byref(h3))
        SDL_QueryTexture(self.time_elapsed_img, None, None, byref(w4), byref(h4))
        dst1 = SDL_Rect(557, 100, w1, h1)
        dst2 = SDL_Rect(500, 450, w2, h2)
        dst3 = SDL_Rect(500, 500, w3, h3)
        dst4 = SDL_Rect(500, 550, w4, h4)
        SDL_RenderCopy(renderer, self.completed_img, None, dst1)
        SDL_RenderCopy(renderer, self.map_completed_img, None, dst2)
        SDL_RenderCopy(renderer, self.respawns, None, dst3)
        SDL_RenderCopy(renderer, self.time_elapsed_img, None, dst4)
        self.back_button.draw(renderer)
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, screen_buffer(), None, None)
        SDL_RenderPresent(renderer)
        return None

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        if self.back_button.hovering:
            self.go_back = True
        return None

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_down(self, key: int) -> None:
        pass

    def on_key_up(self, key: int) -> None:
        pass

    def on_enter(self, data: Any) -> None:
        self.map_completed, self.time_elapsed, self.player_deaths = data
        seconds = self.time_elapsed
        minutes = 0
        hours = 0
        while seconds >= 60:
            seconds -= 60
            minutes += 1
        while minutes >= 60:
            minutes -= 60
            hours += 1
        seconds = round(seconds, 3)
        self.time_elapsed_img = render_utf8_solid_as_texture(
            self.renderer, self.font,
            f"Time elapsed: {hours}h:{minutes}m:{seconds}s".encode(), WHITE
        )
        self.respawns = render_utf8_solid_as_texture(
            self.renderer, self.font, f"Respawns: {self.player_deaths}".encode(), WHITE
        )
        self.map_completed_img = render_utf8_solid_as_texture(
            self.renderer, self.font, f"{self.map_completed} completed".encode(), WHITE
        )

    def quit(self) -> None:
        TTF_CloseFont(self.font)
        SDL_DestroyTexture(self.completed_img)
        if self.map_completed_img is not None:
            SDL_DestroyTexture(self.map_completed_img)
        if self.respawns is not None:
            SDL_DestroyTexture(self.respawns)
        if self.time_elapsed_img is not None:
            SDL_DestroyTexture(self.time_elapsed_img)
        self.back_button.destroy()
