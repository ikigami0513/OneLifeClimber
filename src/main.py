import sys
import pygame
from settings import *
from level import Level
from pytmx.util_pygame import load_pygame
from os.path import join
from support import *
from data import Data
from ui import UI
from overworld import Overworld
from transition import Transition
from gameover_layer import GameoverLayer
from menu import Menu


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("One Life Climber")
        self.clock = pygame.time.Clock()
        self.transition = Transition(self.display_surface)
        self.import_assets()

        self.ui = UI(self.font, self.ui_frames)
        self.game_over_layer = GameoverLayer(self.display_surface, self.reset)
        self.menu = Menu(self.display_surface, on_continue=self.resume_game, on_quit=self.close, on_open=self.open_menu)
        self.data = Data(self.ui, self.create_hat, self.remove_hat)
        self.tmx_maps = {
            0: load_pygame(join('..', 'data', 'levels', 'omni.tmx')),
			1: load_pygame(join('..', 'data', 'levels', '1.tmx')),
			2: load_pygame(join('..', 'data', 'levels', '2.tmx')),
			3: load_pygame(join('..', 'data', 'levels', '3.tmx')),
			4: load_pygame(join('..', 'data', 'levels', '4.tmx')),
			5: load_pygame(join('..', 'data', 'levels', '5.tmx')),
        }
        self.tmx_overworld = load_pygame(join('..', 'data', 'overworld', 'overworld.tmx'))
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.start_stage_transition)
        self.bg_music.play(-1)

    def start_stage_transition(self, target: str, unlock: int = 0):
        if not self.transition.active:
            self.transition.start(
                on_midpoint=lambda: self.switch_stage(target, unlock),
                on_complete=lambda: self.start_level()
            )

    def start_level(self):
        if isinstance(self.current_stage, Level):
            self.current_stage.start()

    def switch_stage(self, target, unlock = 0):
        if target == 'level':
            self.current_stage = Level(self.tmx_maps[self.data.current_level], self.level_frames, self.audio_files, self.data, self.start_stage_transition, self.reset)
        else:  # overworld
            if unlock > 0:
                self.data.unlocked_level = 6
            else:
                self.data.unlocked_level += 1
            
            self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.start_stage_transition)

    def create_hat(self):
        if isinstance(self.current_stage, Level):
            self.current_stage.player.add_hat()

    def remove_hat(self):
        if isinstance(self.current_stage, Level):
            self.current_stage.player.remove_hat()

    def import_assets(self):
        self.level_frames = {
            'flag': import_folder('..', 'graphics', 'level', 'flag'),
			'saw': import_folder('..', 'graphics', 'enemies', 'saw', 'animation'),
			'floor_spike': import_folder('..', 'graphics','enemies', 'floor_spikes'),
			'palms': import_sub_folders('..', 'graphics', 'level', 'palms'),
			'candle': import_folder('..', 'graphics','level', 'candle'),
			'window': import_folder('..', 'graphics','level', 'window'),
			'big_chain': import_folder('..', 'graphics','level', 'big_chains'),
			'small_chain': import_folder('..', 'graphics','level', 'small_chains'),
			'candle_light': import_folder('..', 'graphics','level', 'candle light'),
			'player': import_sub_folders('..', 'graphics','player'),
			'saw': import_folder('..', 'graphics', 'enemies', 'saw', 'animation'),
			'saw_chain': import_image('..',  'graphics', 'enemies', 'saw', 'saw_chain'),
			'helicopter': import_folder('..', 'graphics', 'level', 'helicopter'),
			'boat': import_folder('..',  'graphics', 'objects', 'boat'),
			'spike': import_image('..',  'graphics', 'enemies', 'spike_ball', 'Spiked Ball'),
			'spike_chain': import_image('..',  'graphics', 'enemies', 'spike_ball', 'spiked_chain'),
			'tooth': import_folder('..', 'graphics','enemies', 'tooth', 'run'),
			'shell': import_sub_folders('..', 'graphics','enemies', 'shell'),
			'pearl': import_image('..',  'graphics', 'enemies', 'bullets', 'pearl'),
			'items': import_sub_folders('..', 'graphics', 'items'),
			'particle': import_folder('..', 'graphics', 'effects', 'particle'),
			'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
			'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
			'bg_tiles': import_folder_dict('..', 'graphics', 'level', 'bg', 'tiles'),
			'cloud_small': import_folder('..', 'graphics','level', 'clouds', 'small'),
			'cloud_large': import_image('..', 'graphics','level', 'clouds', 'large_cloud'),
        }

        self.font = pygame.font.Font(join('..', 'graphics', 'ui', 'runescape_uf.ttf'), 40)
        
        self.ui_frames = {
			'coin':import_image('..', 'graphics', 'ui', 'coin'),
            'hat': import_image('..','graphics', 'ui', 'hat')
		}
        
        self.overworld_frames = {
			'palms': import_folder('..', 'graphics', 'overworld', 'palm'),
			'water': import_folder('..', 'graphics', 'overworld', 'water'),
			'path': import_folder_dict('..', 'graphics', 'overworld', 'path'),
			'icon': import_sub_folders('..', 'graphics', 'overworld', 'icon'),
		}

        self.audio_files = {
			'coin': pygame.mixer.Sound(join('..', 'audio', 'coin.wav')),
			'attack': pygame.mixer.Sound(join('..', 'audio', 'attack.wav')),
			'jump': pygame.mixer.Sound(join('..', 'audio', 'jump.wav')), 
			'damage': pygame.mixer.Sound(join('..', 'audio', 'damage.wav')),
			'pearl': pygame.mixer.Sound(join('..', 'audio', 'pearl.wav')),
		}
        self.audio_files["jump"].set_volume(0.2)

        self.bg_music = pygame.mixer.Sound(join('..', 'audio', 'starlight_city.mp3'))
        self.bg_music.set_volume(0.5)

    def check_game_over(self):
        if self.data.health <= 0:
            if isinstance(self.current_stage, Level):
                self.current_stage.pause()
            self.game_over_layer.show()

        elif isinstance(self.current_stage, Level) and self.current_stage.player.hitbox_rect.bottom > self.current_stage.level_bottom:
            self.current_stage.pause()
            self.game_over_layer.show()

    def reset(self):
        self.data = Data(self.ui, self.create_hat, self.remove_hat)
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.start_stage_transition)
        self.game_over_layer.hide()

    def close(self): 
        pygame.quit()
        sys.exit()

    def resume_game(self):
        self.menu.hide()
        if isinstance(self.current_stage, Level):
            self.current_stage.start()

    def open_menu(self):
        self.menu.show()
        if isinstance(self.current_stage, Level):
            self.current_stage.pause()

    def run(self):
        while True:
            dt = self.clock.tick() / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                self.menu.handle_event(event)
                self.game_over_layer.handle_event(event)

            self.check_game_over()
            self.current_stage.run(dt)
            self.ui.update(dt, self.data.health, self.data.coins)
            self.transition.update(dt)
            self.menu.update()
            self.transition.draw()
            self.menu.draw()
            self.game_over_layer.draw()

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
