import pygame
from typing import Callable, Optional


class Transition:
    def __init__(self, screen: pygame.Surface, duration: float = 1.0) -> None:
        self.screen = screen
        self.duration = duration
        self.black_duration = self.duration / 4
        self.half_duration = (duration / 2) - self.black_duration
        self.time = 0.0
        self.active = False
        self.mid_triggered = False
        self.on_midpoint: Callable[[], None] = lambda: None
        self.on_complete: Callable[[], None] = lambda: None
        self.alpha = 0.0

        self.surface = pygame.Surface(self.screen.get_size())
        self.surface.fill((0, 0, 0))
        self.surface.set_alpha(0)

    def start(self, on_midpoint: Callable[[], None], on_complete: Optional[Callable[[], None]] = None) -> None:
        self.time = 0.0
        self.active = True
        self.mid_triggered = False
        self.on_midpoint = on_midpoint
        self.on_complete = on_complete if on_complete else lambda: None

    def update(self, dt: float) -> None:
        if not self.active:
            return
        
        self.time += dt

        # Call midpoint when screen is fully black
        if self.time >= self.half_duration and not self.mid_triggered:
            self.mid_triggered = True
            self.on_midpoint()

        # End of transition
        if self.time >= self.duration:
            self.active = False
            self.on_complete()
            return
        
        # Compute alpha: fade-out then fade-in
        if self.time < self.half_duration:
            self.alpha = alpha = int((self.time / self.half_duration) * 255)
        elif self.time > self.half_duration + 0.5:
            self.alpha = int(((self.duration - self.time) / self.half_duration) * 255)

        self.surface.set_alpha(self.alpha)

    def draw(self) -> None:
        if self.active:
            self.screen.blit(self.surface, (0, 0))
            