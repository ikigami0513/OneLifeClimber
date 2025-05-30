import pygame
from settings import *
from timer_ import Timer
from hat import HatGroup, FallingHat
from data import Data
from math import sin
from typing import Dict, List, Tuple, Union


class Player(pygame.sprite.Sprite):
    def __init__(
        self, pos: Tuple[int, int], groups: Union[pygame.sprite.Group, List[pygame.sprite.Group]], 
        collision_sprites: pygame.sprite.Group, semi_collision_sprites: pygame.sprite.Group, 
        frames: Dict[str, List[pygame.Surface]], data: Data, 
        attack_sound: pygame.Sound, jump_sound: pygame.Sound, level_bottom: int
    ) -> None:
        # general setup
        super().__init__(groups)
        self.z = Z_LAYERS['main']
        self.data = data
        self.level_bottom = level_bottom

        # image
        self.frames, self.frame_index = {key: value for key, value in frames.items() if "hat" not in key}, 0
        self.hat_frames = {key: value for key, value in frames.items() if "hat" in key}
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]

        self.hat_sprites = HatGroup(self.hat_frames)
        self.falling_hats_group = pygame.sprite.Group()

        # rects
        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox_rect.copy()

        # hats
        # On "retire" un chapeau PV car le sprite de base du personnage à déjà un chapeau sur lui
        for i in range(self.data.health - 1):
            self.hat_sprites.add_hat(pos, groups, self.state)

        # movement
        self.direction = pygame.Vector2()
        self.speed = 300
        self.gravity = 1300
        self.jump = False
        self.jump_height = 750
        self.attacking = False

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.on_surface = {
            "floor": False,
            "left": False,
            "right": False
        }
        self.platform = None

        # timer
        self.timers = {
            'wall jump': Timer(400),
			'wall slide block': Timer(250),
			'platform skip': Timer(100),
			'attack block': Timer(500),
			'hit': Timer(400)
        }

        # audio
        self.attack_sound = attack_sound
        self.jump_sound = jump_sound

    def add_hat(self) -> None:
        self.hat_sprites.add_hat(self.rect.topleft, self.groups(), self.state)

    def remove_hat(self) -> None:
        if self.hat_sprites.sprites():
            hat = self.hat_sprites.sprites()[-1]
            self.hat_sprites.remove(hat)

            falling_hat = FallingHat(
                image=hat.image,
                pos=hat.rect.center,
                groups=[self.groups(), self.falling_hats_group]
            )
            hat.kill()

    def input(self) -> None:
        keys = pygame.key.get_pressed()
        input_vector = pygame.Vector2(0, 0)

        if not self.timers['wall jump'].active:
            if keys[pygame.K_d]:
                input_vector.x += 1
                self.facing_right = True

            if keys[pygame.K_q]:
                input_vector.x -= 1
                self.facing_right = False

            if keys[pygame.K_s]:
                self.timers['platform skip'].activate()

            if keys[pygame.K_e]:
                self.attack()

            self.direction.x = input_vector.normalize().x if input_vector else input_vector.x

        if keys[pygame.K_z]:
            self.jump = True

    def attack(self) -> None:
        if not self.timers['attack block'].active:
            self.attacking = True
            self.frame_index = 0
            self.timers['attack block'].activate()
            self.attack_sound.play()

    def move(self, dt: float) -> None:
        # horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision("horizontal")

        # vertical
        if not self.on_surface['floor'] and any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
            self.direction.y = 0
            self.hitbox_rect.y += self.gravity / 10 * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt

        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                self.timers['wall slide block'].activate()
                self.hitbox_rect.bottom -= 1
                self.jump_sound.play()
            elif any((self.on_surface['left'], self.on_surface['right'])) and not self.timers['wall slide block'].active:
                self.timers['wall jump'].activate()
                self.direction.y = -self.jump_height
                self.direction.x = 1 if self.on_surface['left'] else -1
                self.jump_sound.play()
            self.jump = False

        self.collision("vertical")
        self.semi_collision()
        self.rect.center = self.hitbox_rect.center

    def platform_move(self, dt: float) -> None:
        if self.platform:
            self.hitbox_rect.topleft += self.platform.direction * self.platform.speed * dt

    def check_contact(self) -> None:
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft,(self.hitbox_rect.width,2))
        right_rect = pygame.Rect(self.hitbox_rect.topright + pygame.Vector2(0,self.hitbox_rect.height / 4), (2,self.hitbox_rect.height / 2))
        left_rect  = pygame.Rect(self.hitbox_rect.topleft + pygame.Vector2(-2,self.hitbox_rect.height / 4), (2,self.hitbox_rect.height / 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]
        semi_collide_rect = [sprite.rect for sprite in self.semi_collision_sprites]

		# collisions 
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 or floor_rect.collidelist(semi_collide_rect) >= 0 and self.direction.y >= 0 else False
        self.on_surface['right'] = True if right_rect.collidelist(collide_rects) >= 0 else False
        self.on_surface['left']  = True if left_rect.collidelist(collide_rects)  >= 0 else False

        self.platform = None
        sprites =  self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in sprites if hasattr(sprite, 'moving')]:
            if sprite.rect.colliderect(floor_rect):
                self.platform = sprite

    def collision(self, axis: str) -> None:
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == 'horizontal':
					# left
                    if self.hitbox_rect.left <= sprite.rect.right and int(self.old_rect.left) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right

					# right
                    if self.hitbox_rect.right >= sprite.rect.left and int(self.old_rect.right) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                else: # vertical
					# top
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(self.old_rect.top) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        if hasattr(sprite, 'moving'):
                            self.hitbox_rect.top += 6

					# bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    self.direction.y = 0

    def semi_collision(self) -> None:
        if not self.timers['platform skip'].active:
            for sprite in self.semi_collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(self.old_rect.bottom) <= sprite.old_rect.top:
                        self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y > 0:
                            self.direction.y = 0

    def update_timers(self) -> None:
        for timer in self.timers.values():
            timer.update()

    def animate(self, dt: float) -> None:
        self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames[self.state]):
            self.state = 'idle'
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self) -> None:
        if self.on_surface['floor']:
            if self.attacking:
                self.state = 'attack'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'run'
        else:
            if self.attacking:
                self.state = 'air_attack'
            else:
                if any((self.on_surface['left'], self.on_surface['right'])):
                    self.state = 'wall'
                else:
                    self.state = 'jump' if self.direction.y < 0 else 'fall'

    def get_damage(self) -> None:
        if not self.timers['hit'].active:
            self.data.health -= 1
            self.timers['hit'].activate()

    def flicker(self) -> None:
        if self.timers['hit'].active and sin(pygame.time.get_ticks() * 100) >= 0:
            white_mask = pygame.mask.from_surface(self.image)
            white_surf = white_mask.to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def update(self, dt: float) -> None:
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.input()
        self.move(dt)
        self.hat_sprites.update(self.rect.topleft, self.frame_index, self.state, self.facing_right)
        self.falling_hats_group.update(dt, self.level_bottom)
        self.platform_move(dt)
        self.check_contact()

        self.get_state()
        self.animate(dt)
        self.flicker()
        