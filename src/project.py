import pygame
import sys
import random
import time
from enum import Enum

class Scene(Enum):
    MAIN_MENU = 0,
    GAME = 1,
    GAME_OVER = 2

class MainMenu:
    def __init__(self):
        pass

    def get_event(self, event):
        pass

    def draw(self):
        pass

class Map:
    pass

class Game:
    def __init__(self):
        self.map = Map()
        self.game_active = True

    def get_event(self, event):
        pass

    def draw(self):
        pass


class GameOver:
    def __init__(self):
        pass

    def get_event(self, event):
        pass

    def draw(self):
        pass

class StateManager:
    def __init__(self, screen):
        self.screen = screen
        self.main_menu = MainMenu()
        self.game = Game()
        self.game_over = GameOver()
        self.current_scene = Scene.MAIN_MENU
        # images...
        # sounds...

    def set_scene(self, scene):
        self.current_scene = scene

    def get_event(self, event):
        if self.current_scene == Scene.MAIN_MENU:
            self.main_menu.get_event(event)
        elif self.current_scene == Scene.GAME:
            self.game.get_event(event)
        elif self.current_scene == Scene.GAME_OVER:
            self.game_over.get_event(event)

    def draw(self):
        if self.current_scene == Scene.MAIN_MENU:
            self.main_menu.draw()
        elif self.current_scene == Scene.GAME:
            self.game.draw()
        elif self.current_scene == Scene.GAME_OVER:
            self.game_over.draw()

def main():
    pygame.init()

    pygame.display.set_caption("Tank Tower Defense")
    screen = pygame.display.set_mode((640, 480))

    state_manager = StateManager(screen)

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            state_manager.get_event(event)

        state_manager.draw()

        pygame.display.flip()

        clock.tick(60)

main()
