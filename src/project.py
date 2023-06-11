from enum import Enum
import pygame
import sys
import math

# Global variables
pygame.font.init()
font = pygame.font.SysFont("avenir", 16)
click = False
keys = []


# Enums
class State(Enum):
    """Holds a cell's state, open or occupied"""
    OPEN = 0,
    BLOCKED = 1


# Helper functions
def interp(n: int, from1: int, to1: int, from2: int, to2: int):
    """Interpolates a number from one range to another range"""
    return (n - from1) / (to1 - from1) * (to2 - from2) + from2


# Game classes
class Cell:
    """A unit of the map, used for holding towers and pathfinding"""
    def __init__(self, screen, index):
        self.index = index
        self.state = State.OPEN
        self.highlighted = False
        self.screen = screen

    def draw(self, rect):
        color = (255, 255, 255)
        if self.highlighted:
            color = (255, 0, 0)
        pygame.draw.rect(self.screen, color, rect)

class Tank:
    def __init__(self, screen: pygame.Surface, pos: tuple[int, int], base_image: pygame.Surface, turret_image: pygame.Surface, angle: int = 0, size: int = 32):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.image = base_image
        self.angle = angle
        self.size = size
        self.turret = Turret(screen, self, turret_image, angle)

    def draw(self):
        rotated = pygame.transform.rotate(self.image, 90 - self.angle)
        centered_rect = rotated.get_rect(center=(self.x - self.size // 2, self.y - self.size // 2))
        self.screen.blit(rotated, centered_rect)
        self.turret.draw()

    def rotate(self, amount: int):
        self.angle += amount

    def move(self, amount: int):
        x = math.cos(math.radians(self.angle))
        y = math.sin(math.radians(self.angle))
        self.x += x * amount
        self.y += y * amount

class Turret:
    def __init__(self, screen, parent_tank: Tank, default_image: pygame.Surface, angle: int = 0, size: int = -1):
        self.screen = screen
        self.tank = parent_tank
        self.image = default_image
        self.angle = angle
        self.size = size
        self.offset = (0, 0)

    def draw(self):
        size = self.tank.size if self.size == -1 else self.size
        rotated = pygame.transform.rotate(self.image, 90 - self.angle)
        centered_rect = rotated.get_rect(center=((self.tank.x + self.offset[0]) - size // 2, (self.tank.y + self.offset[1]) - size // 2))
        self.screen.blit(rotated, centered_rect)

    def rotate(self, amount: int):
        self.angle += amount

class Map:
    """Contains the list of cells in the grid and performs algorithms on them"""

    def __init__(self, screen: pygame.Surface, size: int = 32):
        self.screen = screen
        self.size = size
        self.grid: list[list[Cell]] = []
        n = self.get_rows()
        for x in range(0, n):
            self.grid.append([])
            for y in range(0, n):
                self.grid[x].append(Cell(self.screen, self.rect_to_index((x, y))))

    def get_rows(self):
        return self.screen.get_width() // self.size

    def draw(self):
        n = self.get_rows()
        for x in range(0, n):
            for y in range(0, n):
                rect = (x * self.size, y * self.size, self.size, self.size)
                self.grid[x][y].draw(rect)

                i = y + x * n
                text = font.render(f"{i}", True, (0, 0, 0))
                text_rect = text.get_rect(center=(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2))
                self.screen.blit(text, text_rect)

    def mouse_to_rect(self, mouse_pos: tuple[int, int]) -> tuple[int, int]:
        x = mouse_pos[0]
        y = mouse_pos[1]
        return x // self.size, y // self.size

    def rect_to_index(self, rect: tuple[int, int]) -> int:
        return rect[0] * self.size + rect[1]

    def mouse_to_index(self, mouse_pos: tuple[int, int]) -> int:
        return self.rect_to_index(self.mouse_to_rect(mouse_pos))

    def index_to_rect(self, index: int) -> tuple[int, int]:
        return index // self.size, index % self.size


class Game:
    """Handles the gameplay, delegation, and processes most events"""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.game_active = True
        self.map = Map(screen)
        self.tanks: list[Tank] = []
        # self.tanks.append(Tank(screen, (200, 200), ))

    def get_event(self, event):
        if click:
            pos = self.map.mouse_to_rect(event.pos)
            self.map.grid[pos[0]][pos[1]].highlighted = True

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.map.draw()

        for tank in self.tanks:
            tank.draw()


class StateManager:
    """Handles menus and the game"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.game = Game(screen)
        # images...
        # sounds...

    def get_event(self, event):
        self.game.get_event(event)

    def draw(self):
        self.game.draw()


def main():
    # Global variables that will be set here
    global click
    global keys

    # Start pygame
    pygame.init()

    # Setup window, screen, and clock
    pygame.display.set_caption("Tank Tower Defense")
    screen = pygame.display.set_mode((640, 640))
    clock = pygame.time.Clock()

    # Set up our game
    state_manager = StateManager(screen)

    # Game loop
    while True:
        # Update keys
        keys = pygame.key.get_pressed()

        # Get and process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            state_manager.get_event(event)

        # Update display
        state_manager.draw()

        # Render entire display
        pygame.display.flip()

        # Progress time
        clock.tick(60)

        # Reset click frame
        click = False


main()
