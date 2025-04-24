import pygame
from os.path import join
from typing import Callable


class GameoverLayer:
    def __init__(self, surface: pygame.Surface, on_restart: Callable[[], None]):
        self.surface = surface
        self.on_restart = on_restart
        self.font = pygame.font.Font(join('..', 'graphics', 'ui', 'runescape_uf.ttf'), 48)
        self.button_font = pygame.font.Font(join('..', 'graphics', 'ui', 'runescape_uf.ttf'), 36)

        self.button_text = "Restart"
        self.button_color = pygame.Color(200, 50, 50)
        self.button_hover_color = pygame.Color(255, 80, 80)
        self.text_color = pygame.Color(255, 255, 255)
        self.bg_color = pygame.Color(0, 0, 0, 180)

        self.button_rect = pygame.Rect(0, 0, 300, 70)
        self.button_rect.center = (surface.get_width() // 2, surface.get_height() // 2 + 50)

        self.visible = False

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.visible:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                self.on_restart()

    def draw(self) -> None:
        if not self.visible:
            return
        
        overlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        overlay.fill(self.bg_color)
        self.surface.blit(overlay, (0, 0))

        title_surface = self.font.render("Game Over", True, self.text_color)
        title_rect = title_surface.get_frect(center = (self.surface.get_width() // 2, self.surface.get_height() // 2 - 50))
        self.surface.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        color = self.button_hover_color if self.button_rect.collidepoint(mouse_pos) else self.button_color

        pygame.draw.rect(self.surface, color, self.button_rect, border_radius=12)

        button_surface = self.button_font.render(self.button_text, True, self.text_color)
        button_rect = button_surface.get_frect(center = self.button_rect.center)
        self.surface.blit(button_surface, button_rect)
        