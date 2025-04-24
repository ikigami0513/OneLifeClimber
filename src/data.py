from ui import UI
from typing import Callable


class Data:
    def __init__(self, ui: UI, create_hat: Callable[[], None], remove_hat: Callable[[], None]) -> None:
        self.ui = ui
        self._coins = 0
        self._health = 2
        self.create_hat = create_hat
        self.remove_hat = remove_hat

        self.unlocked_level = 0
        self.current_level = 0

    @property
    def coins(self) -> int:
        return self._coins
    
    @coins.setter
    def coins(self, value: int) -> None:
        self._coins = value
        if self.coins >= 100:
            self.coins -= 100
            self.health += 1

    @property
    def health(self) -> int:
        return self._health
    
    @health.setter
    def health(self, value: int) -> None:
        if value > self._health:
            self.create_hat()
        elif 0 < value < self._health:
            self.remove_hat()

        self._health = value
        