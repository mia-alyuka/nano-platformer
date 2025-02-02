from ctypes import byref
from useful import *


class Button:
    def __init__(self, renderer: SDL_Renderer, magic_word: str, position: tuple[int, int], window_size: tuple[int, int]) -> None:
        self.window_size = window_size
        self.focused = load_image_as_texture(f"./assets/{magic_word}_focus.png".encode(), renderer)
        self.idle = load_image_as_texture(f"./assets/{magic_word}_idle.png".encode(), renderer)
        wid, hei = c_int(0), c_int(0)
        SDL_QueryTexture(self.focused, None, None, byref(wid), byref(hei))
        self.size = wid.value, hei.value
        self.hovering = False
        if position[0] == -1:
            self.position = 1920 // 2 - self.size[0] // 2, position[1]
        else:
            self.position = position

    def update(self) -> None:
        x, y = c_int(0), c_int(0)
        SDL_GetMouseState(byref(x), byref(y))
        x_scaler = self.window_size[0] / 1920
        y_scaler = self.window_size[1] / 1080
        horizontally_bounded = self.position[0] * x_scaler < x.value < (self.position[0] + self.size[0]) * x_scaler
        vertically_bounded = self.position[1] * y_scaler < y.value < (self.position[1] + self.size[1]) * y_scaler
        self.hovering = horizontally_bounded and vertically_bounded

    def draw(self, renderer: SDL_Renderer) -> None:
        dst = SDL_Rect(
            self.position[0],
            self.position[1],
            self.size[0],
            self.size[1]
        )
        if self.hovering:
            SDL_RenderCopy(renderer, self.focused, None, byref(dst))
        else:
            SDL_RenderCopy(renderer, self.idle, None, byref(dst))

    def destroy(self) -> None:
        SDL_DestroyTexture(self.idle)
        SDL_DestroyTexture(self.focused)
