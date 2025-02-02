from json import load
from ctypes import byref

from sdl2 import *
from sdl2.sdlimage import *

from Intro import Intro
from MainMenu import MainMenu
from Credits import Credits
from MapSelector import MapSelector
from SceneManager import SceneManager
from Loading import Loading
from Platformer import Platformer
from MapCompleted import MapCompleted

import CommonScreenBuffer as ComSB


class Game:
    def __init__(self) -> None:
        with open("settings.json", "r") as cfg:
            self.config: dict = load(cfg)
        self.window_size: tuple[int, int] = self.config["window"]["width"], self.config["window"]["height"]
        self.controls: dict[str, str] = self.config["controls"]
        self.vsync: bool = self.config["window"]["vsync"]
        self.fullscreen: bool = self.config["window"]["fullscreen"]
        self.window_flags = 0
        self.renderer_flags = SDL_RENDERER_ACCELERATED
        if self.fullscreen:
            self.window_flags = SDL_WINDOW_FULLSCREEN
        if self.vsync:
            self.renderer_flags = SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
        self.window = SDL_CreateWindow(
            b"Nano platformer 1.1.0",
            SDL_WINDOWPOS_UNDEFINED,
            SDL_WINDOWPOS_UNDEFINED,
            self.window_size[0],
            self.window_size[1],
            self.window_flags
        )
        self.renderer = SDL_CreateRenderer(self.window, -1, self.renderer_flags)
        ComSB.init(self.renderer)
        SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_BLEND)
        self.window_icon = IMG_Load(b"./assets/player.png")
        SDL_SetWindowIcon(self.window, self.window_icon)
        self.scene_manager = SceneManager()
        scenes = {
            "Intro": Intro(self.window_size, self.renderer),
            "Main menu": MainMenu(self.window_size, self.renderer),
            "Credits": Credits(self.window_size, self.renderer),
            "Map selector": MapSelector(self.window_size, self.renderer),
            "Loading": Loading(self.window_size, self.renderer),
            "Platformer": Platformer(self.window_size, self.controls, self.renderer),
            "Map completed": MapCompleted(self.window_size, self.renderer)
        }
        self.scene_manager.add_scenes(scenes)

    def run(self) -> None:
        alpha = SDL_GetTicks()
        active = True
        while active:
            beta = SDL_GetTicks()
            delta_time = (beta - alpha) / 1000
            alpha = beta
            event = SDL_Event()
            while SDL_PollEvent(byref(event)):
                if event.type == SDL_QUIT:
                    active = False
                elif event.type == SDL_MOUSEBUTTONDOWN:
                    x, y = c_int(0), c_int(0)
                    SDL_GetMouseState(byref(x), byref(y))
                    self.scene_manager.on_mouse_button_down((x, y))
                elif event.type == SDL_MOUSEBUTTONUP:
                    x, y = c_int(0), c_int(0)
                    SDL_GetMouseState(byref(x), byref(y))
                    self.scene_manager.on_mouse_button_up((x, y))
                elif event.type == SDL_KEYDOWN and event.key.repeat == 0:
                    key = event.key.keysym.sym
                    self.scene_manager.on_key_down(key)
                elif event.type == SDL_KEYUP:
                    key = event.key.keysym.sym
                    self.scene_manager.on_key_up(key)
            self.scene_manager.update(delta_time)
            self.scene_manager.draw(self.window, self.renderer)
            if self.scene_manager.should_quit:
                active = False

    def quit(self):
        SDL_DestroyRenderer(self.renderer)
        SDL_DestroyWindow(self.window)
        self.scene_manager.quit()
        ComSB.quit()
