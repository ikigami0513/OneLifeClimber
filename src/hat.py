import pygame
from typing import List, Tuple
from settings import *


class HatGroup(pygame.sprite.Group):
    def __init__(self, frames):
        super().__init__()
        self.frames = frames

    def sprites(self) -> List['Hat']:
        return super().sprites()

    def add_hat(self, pos, groups, state):
        hats_number = len(self.sprites())
        pos = self.get_pos(pos, hats_number, self.frames[f"{state}_hat"][0].get_size()[1])
        self.add(Hat(
            pos, self.frames, [groups], state
        ))

    def get_pos(self, pos, index, height):
        return (pos[0], pos[1] - (height * 0.1 * (index + 1)))  # On surélève chaque chapeau de 10% par rapport au précédent

    def update(self, pos: Tuple[int, int], frame_index, state, facing_right) -> None:
        for i, hat in enumerate(self.sprites()):
            new_pos = self.get_pos(pos, i, hat.image.get_size()[1])
            hat.rect.topleft = new_pos
            hat.update(frame_index, state, facing_right)


class Hat(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, state):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[f"{state}_hat"][int(self.frame_index)]
        self.rect = self.image.get_frect(topleft=pos)
        self.z = Z_LAYERS['main']

    def update(self, frame_index, state, facing_right):
        self.frame_index = frame_index
        self.image = self.frames[f"{state}_hat"][int(self.frame_index) % len(self.frames[f"{state}_hat"])]
        self.image = self.image if facing_right else pygame.transform.flip(self.image, True, False)


class FallingHat(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos: Tuple[int, int], groups: List[pygame.sprite.Group]):
        super().__init__(*groups)
        self.original_image = image
        self.image = image.copy()
        self.rect = self.image.get_frect(center=pos)
        self.velocity = pygame.Vector2(100, -300)
        self.gravity = 1000
        self.rotation = 0
        self.rotation_speed = 360
        self.z = Z_LAYERS['main']

    def update(self, dt: float):
        self.velocity.y += self.gravity * dt
        displacement = self.velocity * dt
        self.rect.centerx += displacement.x
        self.rect.centery += displacement.y
        self.rotation = (self.rotation + self.rotation_speed * dt) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_frect(center=self.rect.center)

        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
