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
        
        original_coin_surf = frames['coin']
        target_height = self.hat_surf.get_height()

        original_width, original_height = original_coin_surf.get_size()
        aspect_ratio = original_width / original_height
        target_width = int(target_height * aspect_ratio)

        self.coin_surf = pygame.transform.scale(original_coin_surf, (target_width, target_height))


    def display_hat(self, amount):
        hat_rect = self.hat_surf.get_frect(topleft = (10, 10))
        text_surf = self.font.render(str(amount), False, '#33323d')
        text_rect = hat_rect.move(self.hat_surf.get_size()[0] + 5, 0)
        self.display_surface.blit(self.hat_surf, hat_rect)
        self.display_surface.blit(text_surf, text_rect)

    def display_coin(self, amount):
        coin_rect = self.coin_surf.get_frect(topleft = (20, 50))
        text_surf = self.font.render(str(amount), False, '#33323d')

        text_rect = coin_rect.move(self.coin_surf.get_size()[0] + 18, 0)
        self.display_surface.blit(self.coin_surf, coin_rect)
        self.display_surface.blit(text_surf, text_rect)

    def update(self, dt: float, hat_amount: int, coin_amount: int):
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        self.display_hat(hat_amount)
        self.display_coin(coin_amount)
