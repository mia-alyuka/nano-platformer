from collections.abc import Callable
from ctypes import byref
from pathlib import Path
from typing import Any
from sdl2 import *
from sdl2.sdlttf import *
from sdl2.sdlimage import *
from useful import load_image_as_texture
from Button import Button
from CommonScreenBuffer import screen_buffer
from Scene import Scene


BLACK = SDL_Color(0, 0, 0, SDL_ALPHA_OPAQUE)
WHITE = SDL_Color(255, 255, 255, SDL_ALPHA_OPAQUE)


class MapSelector(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.window_size: tuple[int, int] = args[0]
        self.renderer = args[1]
        self.start_button = Button(self.renderer, "start", (-1, 800), self.window_size)
        self.previous_map_button = Button(self.renderer, "selector2", (1920 // 2 - 300, 500), self.window_size)
        self.next_map_button = Button(self.renderer, "selector", (1920 // 2 + 300 - 51, 500), self.window_size)
        self.error_map_cover = load_image_as_texture(b"./assets/map_cover_error.png", self.renderer)
        self.font = TTF_OpenFont(b"./assets/TinyUnicode.ttf", 64)
        no_maps_found_surf = TTF_RenderUTF8_Solid(self.font, b"No maps found in the maps folder :(", WHITE)
        self.no_maps_found = SDL_CreateTextureFromSurface(self.renderer, no_maps_found_surf)
        SDL_FreeSurface(no_maps_found_surf)
        self.title_thing = load_image_as_texture(b"./assets/select_map.png", self.renderer)
        self.back_button = Button(self.renderer, "back", (-1, 860), self.window_size)
        self.refresh_button = Button(self.renderer, "refresh", (-1, 920), self.window_size)
        self.should_go_next: str | None = None
        self.map_to_be_played: str | None = None
        self.selected = 0
        self.maps_folder = Path.cwd() / "maps"
        self.maps_paths: list[Path] = []
        self.maps_names: list[str] = []
        self.maps_covers_paths: list[Path] = []
        self.maps_covers_loaded: list[SDL_Texture | None] = []
        self.maps_names_rendered: list[SDL_Texture] = []
        self.maps_count = 0
        self.refresh_maps(self.renderer)

    def refresh_maps(self, renderer) -> None:
        self.maps_paths = [x for x in self.maps_folder.glob("*") if x.is_dir()]
        self.maps_names = [x.name for x in self.maps_paths]
        self.maps_covers_paths: list[Path] = [x / "cover.png" for x in self.maps_paths]
        for i in range(len(self.maps_covers_loaded)):
            SDL_DestroyTexture(self.maps_covers_loaded.pop())
        for map_cover_path in self.maps_covers_paths:
            if map_cover_path.exists():
                raw = IMG_Load(str(map_cover_path).encode())
                raw_tex = SDL_CreateTextureFromSurface(renderer, raw)
                buf_tex = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGB24, SDL_TEXTUREACCESS_TARGET, 384, 216)
                SDL_SetRenderTarget(renderer, buf_tex)
                SDL_RenderCopy(renderer, raw_tex, None, None)
                SDL_FreeSurface(raw)
                SDL_DestroyTexture(raw_tex)
                self.maps_covers_loaded.append(buf_tex)
            else:
                self.maps_covers_loaded.append(None)
        maps_names_rendered_surfs = [TTF_RenderUTF8_Solid(self.font, name.encode(), WHITE) for name in self.maps_names]
        self.maps_names_rendered = [
            SDL_CreateTextureFromSurface(renderer, i) for i in maps_names_rendered_surfs
        ]
        for _ in range(len(maps_names_rendered_surfs)):
            SDL_FreeSurface(maps_names_rendered_surfs.pop())
        self.maps_count = len(self.maps_paths)
        self.selected = 0

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        self.back_button.update()
        self.next_map_button.update()
        self.previous_map_button.update()
        self.start_button.update()
        self.refresh_button.update()
        if self.should_go_next is not None:
            tmp = self.should_go_next
            self.should_go_next = None
            return tmp
        if self.map_to_be_played is not None:
            data_setter(self.map_to_be_played)
            self.map_to_be_played = None
            return "Loading"
        return None

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, screen_buffer())
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
        SDL_RenderClear(renderer)
        dst = SDL_Rect(672, 0,576, 324)
        SDL_RenderCopy(renderer, self.title_thing, None, byref(dst))
        self.back_button.draw(renderer)
        self.refresh_button.draw(renderer)
        if self.maps_count != 0:
            self.previous_map_button.draw(renderer)
            self.next_map_button.draw(renderer)
            self.start_button.draw(renderer)
            cover = self.maps_covers_loaded[self.selected]
            dst_01 = SDL_Rect(768, 400, 384, 216)
            if cover is None:
                SDL_RenderCopy(renderer, self.error_map_cover, None, dst_01)
            else:
                SDL_RenderCopy(renderer, self.maps_covers_loaded[self.selected], None, dst_01)
            selected_rendered_name = self.maps_names_rendered[self.selected]
            w, h = c_int(0), c_int(0)
            SDL_QueryTexture(selected_rendered_name, None, None, byref(w), byref(h))
            x = c_int(1920//2-w.value//2)
            dst_02 = SDL_Rect(x, 700, w, h)
            SDL_RenderCopy(renderer, selected_rendered_name, None, byref(dst_02))
        else:
            w, h = c_int(0), c_int(0)
            SDL_QueryTexture(self.no_maps_found, None, None, byref(w), byref(h))
            dst_03 = SDL_Rect(500, 500, w, h)
            SDL_RenderCopy(renderer, self.no_maps_found, None, byref(dst_03))
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, screen_buffer(), None, None)
        SDL_RenderPresent(renderer)

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        if self.back_button.hovering:
            self.should_go_next = "Main menu"
        elif self.refresh_button.hovering:
            self.refresh_maps(self.renderer)
        elif self.maps_count == 0:
            pass
        elif self.previous_map_button.hovering and self.selected != 0:
            self.selected -= 1
        elif self.next_map_button.hovering and self.selected != self.maps_count - 1:
            self.selected += 1
        elif self.start_button.hovering:
            self.map_to_be_played = self.maps_names[self.selected]

    def on_key_down(self, key: int) -> None:
        pass

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_up(self, key: int) -> None:
        pass

    def on_enter(self, data: Any) -> None:
        self.refresh_maps(self.renderer)

    def quit(self) -> None:
        self.start_button.destroy()
        self.next_map_button.destroy()
        self.previous_map_button.destroy()
        self.back_button.destroy()
        self.refresh_button.destroy()
        TTF_CloseFont(self.font)
        SDL_DestroyTexture(self.error_map_cover)
        SDL_DestroyTexture(self.no_maps_found)
        for _ in range(len(self.maps_covers_loaded)):
            SDL_DestroyTexture(self.maps_covers_loaded.pop())
        for _ in range(len(self.maps_names_rendered)):
            SDL_DestroyTexture(self.maps_names_rendered.pop())
