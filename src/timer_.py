from pygame.time import get_ticks
from typing import Callable


class Timer:
    def __init__(self, duration: int, func: Callable[[], None] = None, repeat: bool = False):
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False
        self.repeat = repeat

    def activate(self) -> None:
        self.active = True
        self.start_time = get_ticks()

    def deactivate(self) -> None:
        self.active = False
        self.start_time = 0
        if self.repeat:
            self.activate()

    def update(self) -> None:
        current_time = get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()
            