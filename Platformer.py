from collections.abc import Callable
from ctypes import byref
from pathlib import Path
from time import time
from typing import Any, cast
from sdl2 import *
from sdl2.sdlttf import *
from sdl2.sdlgfx import *
from sdl2.sdlimage import *
from CommonScreenBuffer import screen_buffer
from Scene import Scene
from ColliderBox import ColliderBox
from SpecialObject import SpecialObject, RespawnPoint, JumpPad, JumpOrb, DashOrb, RoomFinish, Checkpoint
from useful import load_image_as_texture, getpixel


GRAVITY = 1440


class Platformer(Scene):
    def __init__(self, *args, **kwargs) -> None:
        self.font = TTF_OpenFont(b"./assets/TinyUnicode.ttf", 32)
        self.window_size: tuple[int, int] = args[0]
        self.controls: dict[str, Any] = args[1]
        renderer: SDL_Renderer = args[2]
        self.renderer: SDL_Renderer = args[2]
        self.full_jump_release: bool = self.controls["full jump release"]
        self.jump_key = SDL_GetKeyFromName(self.controls["jump"].encode())
        self.left_key = SDL_GetKeyFromName(self.controls["left"].encode())
        self.right_key = SDL_GetKeyFromName(self.controls["right"].encode())
        self.dash_key = SDL_GetKeyFromName(self.controls["dash"].encode())
        self.player_sprite = load_image_as_texture(b"./assets/player.png", renderer)
        self.jump_pad = load_image_as_texture(b"./assets/jump_pad.png", renderer)
        self.jump_orb = load_image_as_texture(b"./assets/jump_orb.png", renderer)
        self.dash_orb = load_image_as_texture(b"./assets/dash_orb.png", renderer)
        self.room_finish = load_image_as_texture(b"./assets/room_finish.png", renderer)
        self.checkpoint_on = load_image_as_texture(b"./assets/checkpoint_on.png", renderer)
        self.checkpoint_off = load_image_as_texture(b"./assets/checkpoint_off.png", renderer)
        self.player_collider = ColliderBox(0, 0, 24, 24)
        self.map_foreground_sprite: SDL_Texture | None = None
        self.loaded_map = ""
        self.immediate_quit = False
        self.room_count = 0
        self.current_room = 0
        self.map_rooms_backgrounds: list[SDL_Texture] = []
        self.map_rooms_walls: list[list[ColliderBox]] = []
        self.map_rooms_specials: list[list[SpecialObject]] = []
        self.momentum_x = 0.0
        self.momentum_y = 0.0
        self.should_jump = False
        self.can_jump = False
        self.grabbing_wall = False
        self.dash_timer = 0.0
        self.can_dash = False
        self.should_dash = False
        self.dash_momentum = 0.0
        self.dash_timeout = 0.0
        self.jump_effect_is_death = False
        self.jump_effect_position: tuple[int, int] = (0, 0)
        self.jump_effect_timer: float = 0
        self.player_deaths = 0
        self.start_time = time()
        self.has_active_checkpoint = False
        self.update_timeout = 0.0
        self.moving_right = False
        self.moving_left = False

    def player_reset(self) -> None:
        self.momentum_y = 0.0
        self.momentum_x = 0.0
        self.can_jump = False
        self.can_dash = False
        self.dash_timer = 0.0
        self.update_timeout = 0.25
        if self.has_active_checkpoint:
            for obj in self.map_rooms_specials[self.current_room]:
                if isinstance(obj, Checkpoint) and obj.active:
                    self.player_collider.x = obj.position[0]
                    self.player_collider.y = obj.position[1]
        else:
            for obj in self.map_rooms_specials[self.current_room]:
                if isinstance(obj, RespawnPoint):
                    self.player_collider.x = obj.position[0]
                    self.player_collider.y = obj.position[1]
                    break

    def player_die(self) -> None:
        self.jump_effect_is_death = True
        self.jump_effect_position = int(self.player_collider.x) + 12, int(self.player_collider.y) + 12
        self.jump_effect_timer = 255
        self.player_reset()
        self.player_deaths += 1

    def update_jump_effect(self, delta_time: float) -> None:
        self.jump_effect_timer -= delta_time * 255 * 2

    def handle_timeout(self, delta_time: float) -> bool:
        if self.update_timeout > 0:
            self.update_timeout -= delta_time
            return True
        return False

    def handle_player_out_of_bounds(self) -> None:
        if (self.player_collider.x < 0
            or self.player_collider.y < 0
            or self.player_collider.x > 1944
            or self.player_collider.y > 1104):
            self.player_die()

    def handle_jump_pad(self, jump_pad: JumpPad) -> None:
        if jump_pad.collider.is_colliding(self.player_collider):
            self.jump_effect_is_death = False
            self.momentum_y = -700
            self.can_jump = True
            self.can_dash = True
            self.jump_effect_position = jump_pad.position[0] + 12, jump_pad.position[1] + 12
            self.jump_effect_timer = 255

    def handle_jump_orb(self, jump_orb: JumpOrb, delta_time: float) -> None:
        jump_orb.inactive_timer -= delta_time
        if jump_orb.collider.is_colliding(self.player_collider) and not self.can_jump and jump_orb.inactive_timer <= 0:
            self.can_jump = True
            jump_orb.inactive_timer = 3

    def handle_dash_orb(self, dash_orb: DashOrb, delta_time: float) -> None:
        dash_orb.inactive_timer -= delta_time
        if dash_orb.collider.is_colliding(self.player_collider) and not self.can_dash and dash_orb.inactive_timer <= 0:
            self.can_dash = True
            dash_orb.inactive_timer = 3

    def handle_jump_and_dash(self, delta_time: float) -> None:
        if self.should_jump:
            if self.can_jump:
                self.player_collider.y -= 1
                self.momentum_y = -600
                self.can_jump = False
            self.should_jump = False
        self.dash_timer -= delta_time
        self.dash_timeout -= delta_time
        if self.should_dash:
            if self.can_dash and self.dash_timeout <= 0 and self.momentum_x != 0:
                self.momentum_y = min(self.momentum_y, 0)
                self.can_dash = False
                self.dash_timer = 0.1
                self.player_collider.y = int(self.player_collider.y + 1)
                self.dash_momentum = self.momentum_x * 4
                self.dash_timeout = 0.12
            self.should_dash = False

    def handle_checkpoint(self, checkpoint: Checkpoint) -> None:
        if not checkpoint.active and checkpoint.collider.is_colliding(self.player_collider):
            if not self.has_active_checkpoint:
                self.has_active_checkpoint = True
                checkpoint.active = True
            else:
                for j in self.map_rooms_specials[self.current_room]:
                    if isinstance(j, Checkpoint) and j.active:
                        j.active = False
                        break
                checkpoint.active = True

    def handle_vertical_movement(self, delta_time: float) -> None:
        if self.dash_timer <= 0:
            self.momentum_y += GRAVITY * delta_time
            self.player_collider.y += self.momentum_y * delta_time
        if self.grabbing_wall:
            if self.momentum_y > 0:
                self.player_collider.y -= self.momentum_y * delta_time
            if self.momentum_y > 0:
                self.momentum_y = 0
        for wall in [w for w in self.map_rooms_walls[self.current_room] if not w.deadly]:
            if wall.is_colliding(self.player_collider):
                if wall.deadly:
                    self.player_die()
                    break
                self.dash_timer = 0
                if self.momentum_y > 0:
                    self.can_jump = True
                    self.can_dash = True
                    while wall.is_colliding(self.player_collider):
                        self.player_collider.y -= 1
                else:
                    while wall.is_colliding(self.player_collider):
                        self.player_collider.y += 1
                self.momentum_y = 0.0

    def handle_horizontal_movement(self, delta_time: float) -> None:
        self.grabbing_wall = False
        if self.dash_timer > 0:
            self.momentum_x = self.dash_momentum
        self.player_collider.x += self.momentum_x * delta_time
        for wall in [w for w in self.map_rooms_walls[self.current_room] if not w.deadly]:
            if wall.is_colliding(self.player_collider):
                if self.momentum_x < 0:
                    while wall.is_colliding(self.player_collider):
                        self.player_collider.x += 1
                else:
                    while wall.is_colliding(self.player_collider):
                        self.player_collider.x -= 1
                self.can_jump = True
                self.can_dash = True
                self.grabbing_wall = True
                self.momentum_x = 0

    def handle_room_finish(self, room_finish: RoomFinish, data_setter: Callable[[Any], None]) -> bool:
        if room_finish.collider.is_colliding(self.player_collider):
            self.current_room += 1
            self.has_active_checkpoint = False
            if self.current_room == self.room_count:
                data_setter((self.loaded_map, time() - self.start_time, self.player_deaths))
                return True
            else:
                self.player_reset()
        return False

    def handle_deadly_walls(self) -> None:
        for wall in [w for w in self.map_rooms_walls[self.current_room] if w.deadly]:
            if wall.is_colliding(self.player_collider):
                self.player_die()
                break

    def handle_player_input(self):
        self.momentum_x = 0.0
        if self.moving_left:
            self.momentum_x -= 336
        if self.moving_right:
            self.momentum_x += 336

    def update(self, data_setter: Callable[[Any], None], delta_time: float) -> None | str:
        if self.immediate_quit:
            self.immediate_quit = False
            return "Map selector"
        self.update_jump_effect(delta_time)
        in_timeout = self.handle_timeout(delta_time)
        if in_timeout:
            return None
        self.handle_player_input()
        for spc_obj in self.map_rooms_specials[self.current_room]:
            match spc_obj:
                case JumpPad():
                    jump_pad = cast(JumpPad, spc_obj)
                    self.handle_jump_pad(jump_pad)
                case JumpOrb():
                    jump_orb = cast(JumpOrb, spc_obj)
                    self.handle_jump_orb(jump_orb, delta_time)
                case DashOrb():
                    dash_orb = cast(DashOrb, spc_obj)
                    self.handle_dash_orb(dash_orb, delta_time)
                case Checkpoint():
                    checkpoint = cast(Checkpoint, spc_obj)
                    self.handle_checkpoint(checkpoint)
                case RoomFinish():
                    room_finish = cast(RoomFinish, spc_obj)
                    has_finished_map = self.handle_room_finish(room_finish, data_setter)
                    if has_finished_map:
                        return "Map completed"
        self.handle_vertical_movement(delta_time)
        self.handle_horizontal_movement(delta_time)
        self.handle_deadly_walls()
        self.handle_jump_and_dash(delta_time)
        return None

    def draw_current_room_special_objects(self, renderer) -> None:
        for spc_obj in self.map_rooms_specials[self.current_room]:
            match spc_obj:
                case JumpPad():
                    jump_pad = cast(JumpPad, spc_obj)
                    dst = SDL_Rect(jump_pad.position[0], jump_pad.position[1], 24, 24)
                    SDL_RenderCopy(renderer, self.jump_pad, None, byref(dst))
                case JumpOrb():
                    jump_orb = cast(JumpOrb, spc_obj)
                    if jump_orb.inactive_timer <= 0:
                        dst = SDL_Rect(jump_orb.position[0], jump_orb.position[1], 24, 24)
                        SDL_RenderCopy(renderer, self.jump_orb, None, byref(dst))
                case DashOrb():
                    dash_orb = cast(DashOrb, spc_obj)
                    if dash_orb.inactive_timer <= 0:
                        dst = SDL_Rect(dash_orb.position[0], dash_orb.position[1], 24, 24)
                        SDL_RenderCopy(renderer, self.dash_orb, None, byref(dst))
                case Checkpoint():
                    checkpoint = cast(Checkpoint, spc_obj)
                    dst = SDL_Rect(checkpoint.position[0], checkpoint.position[1], 24, 24)
                    if checkpoint.active:
                        SDL_RenderCopy(renderer, self.checkpoint_on, None, byref(dst))
                    else:
                        SDL_RenderCopy(renderer, self.checkpoint_off, None, byref(dst))
                case RoomFinish():
                    room_finish = cast(RoomFinish, spc_obj)
                    dst = SDL_Rect(room_finish.collider.x, room_finish.collider.y, 24, 24)
                    SDL_RenderCopy(renderer, self.room_finish, None, byref(dst))

    def draw_jump_effect(self, renderer) -> None:
        if self.jump_effect_timer > 0:
            SDL_SetRenderTarget(renderer, screen_buffer())
            size = int(255 - self.jump_effect_timer) // 2
            alpha = int(self.jump_effect_timer) // 2
            col = (0x0000FF if self.jump_effect_is_death else 0x00FFFF) + alpha * 0x1000000
            filledCircleColor(renderer, self.jump_effect_position[0], self.jump_effect_position[1], size, col)

    def draw(self, window: SDL_Window, renderer: SDL_Renderer) -> None:
        SDL_SetRenderTarget(renderer, screen_buffer())
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE)
        SDL_RenderClear(renderer)
        dst = SDL_Rect(int(self.player_collider.x), int(self.player_collider.y), 24, 24)
        SDL_RenderCopy(renderer, self.map_rooms_backgrounds[self.current_room], None, None)
        self.draw_current_room_special_objects(renderer)
        SDL_RenderCopy(renderer, self.player_sprite, None, dst)
        self.draw_jump_effect(renderer)
        SDL_SetRenderTarget(renderer, None)
        SDL_RenderCopy(renderer, screen_buffer(), None, None)
        SDL_RenderPresent(renderer)


    def on_mouse_button_down(self, position: tuple[int, int]) -> None:
        return None

    def on_key_down(self, key: int) -> None:
        if key == SDLK_ESCAPE:
            self.immediate_quit = True
        elif key == self.jump_key:
            self.should_jump = True
        elif key == self.dash_key:
            self.should_dash = True
        elif key == SDLK_r:
            self.load_map()
        elif key == self.right_key:
            self.moving_right = True
        elif key == self.left_key:
            self.moving_left = True
        return None

    @staticmethod
    def extract_specials(obj: SDL_Surface) -> list[SpecialObject]:
        specials: list[SpecialObject] = []
        for x in range(80):
            for y in range(45):
                rx = x * 24
                ry = y * 24
                col = getpixel(obj, x, y)
                match col:
                    case (255, 255, 0):
                        specials.append(RespawnPoint(
                            (rx, ry)
                        ))
                    case (0, 255, 0):
                        specials.append(JumpPad(
                            (rx, ry),
                            ColliderBox(rx, ry + 18, 24, 6)
                        ))
                    case (0, 0, 255):
                        specials.append(JumpOrb(
                            (rx, ry),
                            ColliderBox(rx + 4, ry + 4, 16, 16)
                        ))
                    case (255, 0, 255):
                        specials.append(DashOrb(
                            (rx, ry),
                            ColliderBox(rx + 4, ry + 4, 16, 16)
                        ))
                    case (0, 255, 255):
                        specials.append(RoomFinish(
                            ColliderBox(rx, ry, 24, 24)
                        ))
                    case (0, 127, 127):
                        specials.append(Checkpoint(
                            (rx, ry),
                            ColliderBox(rx + 6, ry + 6, 14, 17)
                        ))
                    case _:
                        pass
        return specials

    @staticmethod
    def extract_walls(obj: SDL_Surface) -> list[ColliderBox]:
        walls = []
        for x in range(80):
            for y in range(45):
                rx = x * 24
                ry = y * 24
                col = getpixel(obj, x, y)
                match col:
                    case (255, 255, 255):
                        walls.append(ColliderBox(rx, ry, 24, 24, False))
                    case (255, 0, 0):
                        walls.append(ColliderBox(rx, ry, 24, 24, True))
                    case _:
                        pass
        return walls

    def load_map(self) -> bool:
        self.current_room = 0
        self.player_deaths = 0
        self.map_rooms_backgrounds = []
        self.map_rooms_walls = []
        self.map_rooms_specials = []
        self.room_count = len([i for i in (Path.cwd() / "maps" / self.loaded_map).glob("*")]) // 2
        for i in range(1, self.room_count + 1):
            bg_path = Path.cwd() / "maps" / self.loaded_map / f"bg{i}.png"
            obj_path = Path.cwd() / "maps" / self.loaded_map / f"obj{i}.png"
            bg_surf = IMG_Load(str(bg_path).encode())
            bg = SDL_CreateTextureFromSurface(self.renderer, bg_surf)
            SDL_FreeSurface(bg_surf)
            self.map_rooms_backgrounds.append(bg)
            obj = IMG_Load(str(obj_path).encode())
            normal = SDL_ConvertSurfaceFormat(obj, SDL_PIXELFORMAT_RGB24, 0)
            SDL_FreeSurface(obj)
            self.map_rooms_walls.append(self.__class__.extract_walls(normal))
            self.map_rooms_specials.append(self.__class__.extract_specials(normal))
            SDL_FreeSurface(normal)
        self.has_active_checkpoint = False
        self.player_reset()
        self.start_time = time()
        return True

    def on_enter(self, data: Any) -> None:
        self.loaded_map = str(data)
        self.load_map()

    def on_mouse_button_up(self, position: tuple[int, int]) -> None:
        pass

    def on_key_up(self, key: int) -> None:
        if key == self.jump_key and self.momentum_y < 0:
            if self.full_jump_release:
                self.momentum_y = 0
            else:
                self.momentum_y /= 3
        elif key == self.left_key:
            self.moving_left = False
        elif key == self.right_key:
            self.moving_right = False

    def quit(self) -> None:
        TTF_CloseFont(self.font)
        SDL_DestroyTexture(self.player_sprite)
        SDL_DestroyTexture(self.jump_orb)
        SDL_DestroyTexture(self.jump_pad)
        SDL_DestroyTexture(self.dash_orb)
        SDL_DestroyTexture(self.checkpoint_on)
        SDL_DestroyTexture(self.checkpoint_off)
        SDL_DestroyTexture(self.room_finish)
        for _ in range(len(self.map_rooms_backgrounds)):
            SDL_DestroyTexture(self.map_rooms_backgrounds.pop())