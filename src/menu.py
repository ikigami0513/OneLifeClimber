import pygame
from os.path import join
from typing import Callable


class Menu:
    def __init__(self, surface: pygame.Surface, on_continue: Callable[[], None], on_quit: Callable[[], None], on_open: Callable[[], None]):
        self.surface = surface
        self.on_continue = on_continue
        self.on_quit = on_quit
        self.on_open = on_open

        self.font = pygame.font.Font(join('..', 'graphics', 'ui', 'runescape_uf.ttf'), 48)
        self.button_font = pygame.font.Font(join('..', 'graphics', 'ui', 'runescape_uf.ttf'), 36)

        self.bg_color = (0, 0, 0, 180)
        self.text_color = (255, 255, 255)
        self.button_color = (50, 150, 50)
        self.button_hover_color = (80, 200, 80)
        self.quit_color = (150, 50, 50)
        self.quit_hover_color = (200, 80, 80)

        self.visible = False

        self.continue_button = pygame.Rect(0, 0, 300, 70)
        self.quit_button = pygame.Rect(0, 0, 300, 70)

        self.continue_button.center = (surface.get_width() // 2, surface.get_height() // 2 - 50)
        self.quit_button.center = (surface.get_width() // 2, surface.get_height() // 2 + 50)

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if not self.visible:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.continue_button.collidepoint(event.pos):
                self.on_continue()
            elif self.quit_button.collidepoint(event.pos):
                self.on_quit()

    def update(self):
        keys = pygame.key.get_just_pressed()

        if keys[pygame.K_ESCAPE] and not self.visible:
            self.on_open()

    def draw(self) -> None:
        if not self.visible:
            return
        
        overlay_width = self.surface.get_width() * 0.3
        overlay_height = self.surface.get_height() * 0.5
        overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))
        pygame.draw.rect(overlay, self.bg_color, overlay.get_rect(), border_radius=20)
        self.surface.blit(overlay, (self.surface.get_width() * 0.35, self.surface.get_height() * 0.25))

        title_surface = self.font.render("Main Menu", True, self.text_color)
        title_rect = title_surface.get_frect(center = (self.surface.get_width() // 2, self.surface.get_height() // 2 - 130))
        self.surface.blit(title_surface, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        continue_color = self.button_hover_color if self.continue_button.collidepoint(mouse_pos) else self.button_color
        pygame.draw.rect(self.surface, continue_color, self.continue_button, border_radius=12)

        continue_text = self.button_font.render("Continue", True, self.text_color)
        continue_rect = continue_text.get_frect(center = self.continue_button.center)
        self.surface.blit(continue_text, continue_rect)

        quit_color = self.quit_hover_color if self.quit_button.collidepoint(mouse_pos) else self.quit_color
        pygame.draw.rect(self.surface, quit_color, self.quit_button, border_radius=12)

        quit_text = self.button_font.render("Quit", True, self.text_color)
        quit_rect = quit_text.get_rect(center=self.quit_button.center)
        self.surface.blit(quit_text, quit_rect)
