from enum import Enum
import pygame
import sys
import math
import random

# Global variables
pygame.font.init()
state_manager = None
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

def equals(a: float, b: float, within: float):
    """Checks if two numbers are equal within a certain tolerance."""
    return abs(a - b) <= within

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
    def __init__(self, screen: pygame.Surface, pos: tuple[int, int], base_image: pygame.Surface,
                 turret_image: pygame.Surface, speed: float = 1, angle: float = 0, size: int = 32):
        self.screen = screen
        self.x = pos[0]
        self.y = pos[1]
        self.image = base_image
        self.angle = angle
        self.size = size
        self.turret = Turret(screen, self, turret_image, angle + 180)

        # Targeting
        self.moving = True
        self.speed = speed
        self.target_pos = pos
        self.target_angle = self.angle

    def update(self):
        if self.moving:
            sin = math.sin(math.radians(self.target_angle - self.angle))
            targeted = equals(0, sin, 0.2)
            if targeted:
                self.rotate_instant(self.target_angle)

                dist = math.sqrt(math.pow(self.x - self.target_pos[0], 2) + math.pow(self.y - self.target_pos[1], 2))
                close = equals(0, dist, self.speed * 1.2)
                if close:
                    self.move_instant(self.target_pos)
                else:
                    self.move_by(self.speed)
            else:
                amount = abs(sin) / sin * 3
                self.rotate_by(amount)

    def draw(self):
        rotated = pygame.transform.rotate(self.image, 90 - self.angle)
        centered_rect = rotated.get_rect(center=(self.x - self.size // 2, self.y - self.size // 2))
        self.screen.blit(rotated, centered_rect)
        self.turret.draw()

    def angle_to_target(self):
        return math.degrees(math.atan2(self.target_pos[1] - self.y, self.target_pos[0] - self.x))

    def rotate_by(self, amount: float):
        self.angle += amount
        self.turret.rotate_by(amount)

    def move_by(self, amount: float):
        x = math.cos(math.radians(self.angle))
        y = math.sin(math.radians(self.angle))
        self.x += x * amount
        self.y += y * amount

    def move_to(self, pos: tuple[float, float], calculate_angle: bool = True):
        self.target_pos = pos
        if calculate_angle:
            self.rotate_to(self.angle_to_target())

    def rotate_to(self, angle: float):
        self.target_angle = angle

    def move_instant(self, pos: tuple[float, float]):
        self.x = pos[0]
        self.y = pos[1]

    def rotate_instant(self, angle: float):
        self.angle = angle

class Turret:
    def __init__(self, screen: pygame.Surface, parent_tank: Tank, default_image: pygame.Surface, angle: float = 0,
                 size: int = -1):
        self.screen = screen
        self.tank = parent_tank
        self.image = default_image
        self.angle = angle
        self.size = size
        self.offset = (0, 0)

    def draw(self):
        size = self.tank.size if self.size == -1 else self.size
        rotated = pygame.transform.rotate(self.image, 90 - self.angle)
        centered_rect = rotated.get_rect(
            center=((self.tank.x + self.offset[0]) - size // 2, (self.tank.y + self.offset[1]) - size // 2))
        self.screen.blit(rotated, centered_rect)

    def rotate_by(self, amount: float):
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

        self.tanks.append(Tank(screen, (200, 200), pygame.image.load("../images/Tank_Base.png"), pygame.image.load("../images/Tank_Turret.png")))

    def get_event(self, event):
        if click:
            pos = self.map.mouse_to_rect(event.pos)
            self.map.grid[pos[0]][pos[1]].highlighted = True
            self.tanks[0].move_to((random.randint(0, 640), random.randint(0, 640)))

    def update(self):
        # # Drive tank with keys
        # if keys[pygame.K_RIGHT]:
        #     self.tanks[0].rotate_by(2)
        # if keys[pygame.K_LEFT]:
        #     self.tanks[0].rotate_by(-2)
        # if keys[pygame.K_UP]:
        #     self.tanks[0].move_by(1)
        # if keys[pygame.K_a]:
        #     self.tanks[0].turret.rotate_by(-2)
        # if keys[pygame.K_d]:
        #     self.tanks[0].turret.rotate_by(2)

        for tank in self.tanks:
            tank.update()

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

    def update(self):
        self.game.update()
        self.game.draw()


def main():
    # Global variables that will be set here
    global state_manager
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
    run = True
    while run:
        # Get actively pressed keys
        keys = pygame.key.get_pressed()

        # Get and process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            state_manager.get_event(event)

        # Update game
        state_manager.update()

        # Render entire display
        pygame.display.flip()

        # Progress time
        clock.tick(60)

        # Reset click frame
        click = False

    # Exit game after loop
    pygame.quit()
    sys.exit()


main()
