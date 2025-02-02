from sdl2 import *


_screen_buffer: SDL_Texture | None = None

def init(renderer: SDL_Renderer):
    global _screen_buffer
    _screen_buffer = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_RGBA32, SDL_TEXTUREACCESS_TARGET, 1920, 1080)
    SDL_SetTextureBlendMode(_screen_buffer, SDL_BLENDMODE_BLEND)

def quit():
    global _screen_buffer
    SDL_DestroyTexture(_screen_buffer)

def screen_buffer():
    return _screen_buffer
