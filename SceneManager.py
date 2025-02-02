from typing import Any
from sdl2 import *
from Scene import Scene


class SceneManager:
    def __init__(self) -> None:
        self.scenes: dict[str, Scene] = {}
        self.active_scene: str = ""
        self.should_quit = False
        self.data: Any = None

    def set_active_scene(self, name: str) -> None:
        if not name in self.scenes:
            raise ValueError(f"Scene named \"{name}\" does not exist")
        self.active_scene = name

    def add_scene(self, scene: Scene, name: str) -> None:
        if name in self.scenes:
            raise ValueError(f"Scene named {name} already exists")
        self.scenes[name] = scene
        if self.active_scene == "":
            self.active_scene = name

    def add_scenes(self, scenes: dict[str, Scene]) -> None:
        for name, scene in scenes.items():
            self.add_scene(scene, name)

    def update(self, delta_time: float) -> None:
        ret = self.scenes[self.active_scene].update(self.data_setter, delta_time)
        if ret is not None:
            if ret == "SceneManager Quit":
                self.should_quit = True
            else:
                self.set_active_scene(ret)
                self.scenes[self.active_scene].on_enter(self.data)
                self.data = None

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        self.scenes[self.active_scene].draw(window, renderer)

    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        self.scenes[self.active_scene].on_mouse_button_down(position)

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        self.scenes[self.active_scene].on_mouse_button_up(position)

    def on_key_down(self, key: int) -> None:
        self.scenes[self.active_scene].on_key_down(key)

    def on_key_up(self, key: int) -> None:
        self.scenes[self.active_scene].on_key_up(key)

    def data_setter(self, data: Any) -> None:
        self.data = data

    def quit(self) -> None:
        for scene in self.scenes.values():
            scene.quit()
