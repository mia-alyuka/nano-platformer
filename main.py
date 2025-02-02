#!/usr/bin/env python3
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from Game import Game


def main() -> None:
    SDL_Init(SDL_INIT_VIDEO)
    IMG_Init(IMG_INIT_PNG)
    TTF_Init()
    game = Game()
    game.run()
    game.quit()
    TTF_Quit()
    IMG_Quit()
    SDL_Quit()


if __name__ == "__main__":
    main()
