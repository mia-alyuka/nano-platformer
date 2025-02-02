from ctypes import cast, POINTER, c_uint8
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *


def load_image_as_texture(file: bytes, renderer: SDL_Renderer) -> SDL_Texture:
    surf: SDL_Surface = IMG_Load(file)
    texture = SDL_CreateTextureFromSurface(renderer, surf)
    SDL_FreeSurface(surf)
    SDL_SetRenderTarget(renderer, texture)
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND)
    SDL_SetRenderTarget(renderer, None)
    return texture


def getpixel(surface: SDL_Surface, x: int, y: int):
    pos = y * 240 + x * 3
    pixels = cast(surface.contents.pixels, POINTER(c_uint8))
    red, green, blue = pixels[pos:pos+3]
    return red, green, blue

def render_utf8_solid_as_texture(renderer: SDL_Renderer, font: TTF_Font, text: bytes, color: SDL_Color) -> SDL_Texture:
    surf = TTF_RenderUTF8_Solid(font, text, color)
    tex = SDL_CreateTextureFromSurface(renderer, surf)
    SDL_FreeSurface(surf)
    return tex
