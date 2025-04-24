import pygame
from settings import *
from data import Data
from math import sin, cos, radians
from random import randint
from typing import Tuple, Optional, Union, List, Dict


class Sprite(pygame.sprite.Sprite):
    def __init__(
        self, pos: Tuple[int, int], surf: pygame.Surface = pygame.Surface((TILE_SIZE, TILE_SIZE)), 
        groups: Optional[Union[List[pygame.sprite.Group], pygame.sprite.Group]] = None, z: int = Z_LAYERS['main']
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()
        self.z = z


class AnimatedSprite(Sprite):
    def __init__(
        self, pos: Tuple[int, int], frames: List[pygame.Surface], 
        groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], 
        z: int = Z_LAYERS['main'], animation_speed: int = ANIMATION_SPEED
    ) -> None:
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups, z)
        self.animation_speed = animation_speed

    def animate(self, dt: float) -> None:
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt: float) -> None:
        self.animate(dt)


class Item(AnimatedSprite):
    def __init__(
        self, item_type: str, pos: Tuple[int, int], frames: List[pygame.Surface], 
        groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], data: Data
    ) -> None:
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.item_type = item_type
        self.data = data

    def activate(self) -> None:
        if self.item_type == 'gold':
            self.data.coins += 5
        if self.item_type == 'silver':
            self.data.coins += 1
        if self.item_type == 'diamond':
            self.data.coins += 20
        if self.item_type == 'skull':
            self.data.coins += 50
        if self.item_type == 'potion':
            self.data.health += 1


class ParticleEffectSprite(AnimatedSprite):
    def __init__(
        self, pos: Tuple[int, int], frames: List[pygame.Surface], 
        groups: Union[List[pygame.sprite.Group], pygame.sprite.Group]
    ) -> None:
        super().__init__(pos, frames, groups)
        self.rect.center = pos
        self.z = Z_LAYERS['fg']

    def animate(self, dt: float) -> None:
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


class MovingSprite(AnimatedSprite):
    def __init__(
        self, frames: List[pygame.Surface], groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], 
        start_pos: Tuple[int, int], end_pos: Tuple[int, int], move_dir: str, speed: int, flip: bool = False
    ) -> None:
        super().__init__(start_pos, frames, groups)
        if move_dir == 'x':
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos

        self.start_pos = start_pos
        self.end_pos = end_pos

        # movement
        self.moving = True
        self.speed = speed
        self.direction = pygame.math.Vector2(1, 0) if move_dir == 'x' else pygame.math.Vector2(0, 1)
        self.move_dir = move_dir

        self.flip = flip
        self.reverse = {
            "x": False,
            "y": False
        }

    def check_border(self) -> None:
        if self.move_dir == 'x':
            if self.rect.right >= self.end_pos[0] and self.direction.x == 1:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            if self.rect.left <= self.start_pos[0] and self.direction.x == -1:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            self.reverse['x'] = True if self.direction.x < 0 else False
        else:
            if self.rect.bottom >= self.end_pos[1] and self.direction.y == 1:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            if self.rect.top <= self.start_pos[1] and self.direction.y == -1:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            self.reverse['y'] = True if self.direction.y > 0 else False

    def update(self, dt: float) -> None:
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * dt
        self.check_border()

        self.animate(dt)
        if self.flip:
            self.image = pygame.transform.flip(self.image, self.reverse['x'], self.reverse['y'])


class Spike(Sprite):
    def __init__(
        self, pos: Tuple[int, int], surf: pygame.Surface, 
        groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], radius: int, speed: int, 
        start_angle: int, end_angle: int, z: int = Z_LAYERS['main']
    ) -> None:
        self.center = pos
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.angle = self.start_angle
        self.direction = 1
        self.full_circle = True if self.end_angle == -1 else False

        # trigonometry
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        
        super().__init__((x, y), surf, groups, z)

    def update(self, dt: float) -> None:
        self.angle += self.direction * self.speed * dt

        if not self.full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle < self.start_angle:
                self.direction = 1

        y = self.center[1] + sin(radians(self.angle)) * self.radius
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        self.rect.center = (x, y)


class Cloud(Sprite):
    def __init__(
        self, pos: Tuple[int, int], surf: pygame.Surface, 
        groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], z: int = Z_LAYERS['clouds']
    ) -> None:
        super().__init__(pos, surf, groups, z)
        self.speed = randint(50, 120)
        self.direction = -1
        self.rect.midbottom = pos

    def update(self, dt: float) -> None:
        self.rect.x += self.direction * self.speed * dt

        if self.rect.right <= 0:
            self.kill()


class Node(pygame.sprite.Sprite):
    def __init__(
        self, pos: Tuple[int, int], surf: pygame.Surface, groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], 
        level: int, data: Data, paths: Dict[str, str]
    ) -> None:
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (pos[0] + TILE_SIZE / 2, pos[1] + TILE_SIZE / 2))
        self.z = Z_LAYERS['path']
        self.level = level
        self.data = data
        self.paths = paths
        self.grid_pos = (int(pos[0] / TILE_SIZE), int(pos[1] / TILE_SIZE))

    def can_move(self, direction: str) -> bool:
        return direction in list(self.paths.keys()) and int(self.paths[direction][0][0]) <= self.data.unlocked_level
        

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[int, int], groups: Union[List[pygame.sprite.Group]], frames: List[pygame.Surface]) -> None:
        super().__init__(groups)
        self.icon = True
        self.path = None
        self.direction = pygame.Vector2()
        self.speed = 400

        # image
        self.frames, self.frame_index = frames, 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.z = Z_LAYERS['main']

        # rect
        self.rect = self.image.get_frect(center = pos)

    def start_move(self, path: List[Tuple[int, int]]) -> None:
        self.rect.center = path[0]
        self.path = path[1:]
        self.find_path()

    def find_path(self) -> None:
        if self.path:
            if self.rect.centerx == self.path[0][0]:  # vertical
                self.direction = pygame.Vector2(0, 1 if self.path[0][1] > self.rect.centery else - 1)
            else: # horizontal
                self.direction = pygame.Vector2(1 if self.path[0][0] > self.rect.centerx else - 1, 0)
        else:
            self.direction = pygame.Vector2()

    def point_collision(self) -> None:
        if self.direction.y == 1 and self.rect.centery >= self.path[0][1] or \
		    self.direction.y == -1 and self.rect.centery <= self.path[0][1]:
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_path()

        if self.direction.x == 1 and self.rect.centerx >= self.path[0][0] or \
		    self.direction.x == -1 and self.rect.centerx <= self.path[0][0]:
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_path()

    def animate(self, dt: float) -> None:
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]

    def get_state(self) -> None:
        self.state = 'idle'
        if self.direction == pygame.Vector2(1, 0):
            self.state = 'right'
        if self.direction == pygame.Vector2(-1, 0):
            self.state = 'left'
        if self.direction == pygame.Vector2(0, 1):
            self.state = 'down'
        if self.direction == pygame.Vector2(0, -1):
            self.state = 'up'

    def update(self, dt: float) -> None:
        if self.path:
            self.point_collision()
            self.rect.center += self.direction * self.speed * dt
        self.get_state()
        self.animate(dt)


class PathSprite(Sprite):
    def __init__(
        self, pos: Tuple[int, int], surf: pygame.Surface, 
        groups: Union[List[pygame.sprite.Group], pygame.sprite.Group], level: int
    ) -> None:
        super().__init__(pos, surf, groups, Z_LAYERS['path'])
        self.level = level
        