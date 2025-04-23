import pygame
from settings import *
from sprites import AnimatedSprite
from random import randint
from timer_ import Timer


class UI:
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        # health / hearts
        self.hat_surf = frames['hat']

        # coins
        self.coin_amount = 0
        self.coin_timer = Timer(1000)
        self.coin_surf = frames['coin']

    def display_hat(self, amount):
        hat_rect = self.hat_surf.get_frect(topleft = (10, 10))
        text_surf = self.font.render(str(amount), False, '#33323d')
        text_rect = hat_rect.move(self.hat_surf.get_size()[0] + 5, 0)
        self.display_surface.blit(self.hat_surf, hat_rect)
        self.display_surface.blit(text_surf, text_rect)

    def display_text(self):
        if self.coin_timer.active:
            text_surf = self.font.render(str(self.coin_amount), False, '#33323d')
            text_rect = text_surf.get_frect(topleft = (16,34))
            self.display_surface.blit(text_surf, text_rect)

            coin_rect = self.coin_surf.get_frect(center = text_rect.bottomleft).move(0,-6)
            self.display_surface.blit(self.coin_surf, coin_rect)

    def show_coins(self, amount):
        self.coin_amount = amount
        self.coin_timer.activate()

    def update(self, dt: float, hat_amount: int):
        self.coin_timer.update()
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_hat(hat_amount)
        self.display_text()


class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt: float):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.active = False
            self.frame_index = 0

    def update(self, dt: float):
        if self.active:
            self.animate(dt)
        else:
            if randint(0, 2000) == 1:
                self.active = True
                