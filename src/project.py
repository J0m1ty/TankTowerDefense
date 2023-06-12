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


class TrackingMode(Enum):
    NONE = 0,
    ANGLE = 1,
    POSITION = 2


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
        self.value = -1

    def draw(self, rect):
        color = (255, 255, 255)
        if self.highlighted:
            color = (255, 0, 0)
        pygame.draw.rect(self.screen, color, rect)

class Tank:
    def __init__(self, screen: pygame.Surface, pos: tuple[int, int], base_image: pygame.Surface,
                 turret_image: pygame.Surface, speed: float = 1, rot_speed: float = 2, turret_rot_speed: float = 3,
                 angle: float = 0, size: int = 32):
        self.screen = screen
        self.pos = pos
        self.image = base_image
        self.angle = angle
        self.size = size
        self.turret = Turret(screen, self, turret_image, turret_rot_speed)
        self.projectiles: list[Projectile] = []
        self.fire_timer = 0

        # Targeting
        self.moving = True
        self.speed = speed
        self.target_pos = pos
        self.rot_speed = rot_speed
        self.target_angle = self.angle

    def get_angle(self):
        return 90 - self.angle

    def get_center(self):
        return self.pos[0] - self.size / 2, self.pos[1] - self.size / 2

    def shoot(self):
        self.projectiles.append(Projectile(self.screen, self, 10, 2))
        self.fire_timer = 8

    def update(self):
        if self.moving:
            sin = math.sin(math.radians(self.target_angle - self.angle))
            targeted = round(sin * 20) / 20 == 0
            if targeted:
                self.rotate_instant(self.target_angle)

                center = self.get_center()
                dist = math.sqrt(
                    math.pow(center[0] - self.target_pos[0], 2) + math.pow(center[1] - self.target_pos[1], 2))
                close = equals(0, dist, self.speed * 1.1)
                if close:
                    self.move_instant((self.target_pos[0] + self.size / 2, self.target_pos[1] + self.size / 2))
                else:
                    self.move_by(self.speed)
            else:
                amount = abs(sin) / sin * self.rot_speed
                self.rotate_by(amount)

            self.turret.update()

            for projectile in self.projectiles:
                projectile.update()

            if self.fire_timer > 0:
                self.fire_timer -= 1

    def draw(self):
        center = self.get_center()
        rotated = pygame.transform.rotate(self.image, self.get_angle())
        centered_rect = rotated.get_rect(center=(center[0], center[1]))
        self.screen.blit(rotated, centered_rect)
        self.turret.draw()
        for projectile in self.projectiles:
            projectile.draw()
        if self.fire_timer > 0:
            self.turret.fire.draw()

    def angle_to_target(self):
        center = self.get_center()
        return math.degrees(math.atan2(self.target_pos[1] - center[1], self.target_pos[0] - center[0]))

    def rotate_by(self, amount: float):
        self.angle += amount

    def move_by(self, amount: float):
        x = math.cos(math.radians(self.angle))
        y = math.sin(math.radians(self.angle))
        self.pos = (self.pos[0] + (x * amount), self.pos[1] + (y * amount))

    def move_to(self, pos: tuple[float, float], calculate_angle: bool = True):
        self.target_pos = pos
        if calculate_angle:
            self.rotate_to(self.angle_to_target())

    def rotate_to(self, angle: float):
        self.target_angle = angle

    def move_instant(self, pos: tuple[float, float]):
        self.pos = pos

    def rotate_instant(self, angle: float):
        self.angle = angle

class Projectile:
    def __init__(self, screen: pygame.Surface, tank: Tank, speed: float, size: int):
        self.screen = screen
        self.tank = tank
        self.pos = tank.turret.get_barrel()
        self.angle = tank.turret.get_angle()
        self.speed = speed
        self.size = size

    def draw(self):
        pygame.draw.circle(self.screen, (2, 2, 2), self.pos, self.size)

    def update(self):
        x = self.pos[0] + self.speed * math.cos(math.radians(-90 - self.angle))
        y = self.pos[1] + self.speed * math.sin(math.radians(-90 - self.angle))
        self.pos = (x, y)

class Turret:
    def __init__(self, screen: pygame.Surface, parent_tank: Tank, default_image: pygame.Surface,
                 turret_rot_speed: float = 3, angle: float = 0, size: int = -1):
        self.screen = screen
        self.tank = parent_tank
        self.fire = Fire(screen, self, pygame.image.load("../images/Fire.png"))
        self.image = default_image
        self.pos_offset = (0, 0)
        self.angle_offset = angle
        self.size = size

        # Targeting
        self.turret_rot_speed = turret_rot_speed
        self.target_angle = 0

    def get_size(self) -> int:
        return self.tank.size if self.size == -1 else self.size

    def get_angle(self) -> float:
        return self.tank.get_angle() + (90 - self.angle_offset) + 180

    def get_center(self) -> tuple[float, float]:
        size = self.get_size()
        return (self.tank.pos[0] + self.pos_offset[0]) - size / 2, (self.tank.pos[1] + self.pos_offset[1]) - size / 2

    def get_barrel(self) -> tuple[float, float]:
        center = self.get_center()
        return center[0] + (self.tank.size / 2) * math.cos(math.radians(-90 - self.get_angle())), center[1] + (self.tank.size / 2) * math.sin(math.radians(-90 - self.get_angle()))

    def update(self):
        sin = math.sin(math.radians(self.target_angle - (self.angle_offset - self.tank.get_angle())))
        targeted = round(sin * 20) / 20 == 0
        if not targeted:
            amount = abs(sin) / sin * self.turret_rot_speed
            self.rotate_by(amount)

    def draw(self):
        center = self.get_center()
        rotated = pygame.transform.rotate(self.image, self.get_angle())
        centered_rect = rotated.get_rect(center=(center[0], center[1]))
        self.screen.blit(rotated, centered_rect)

    def rotate_by(self, amount: float):
        self.angle_offset += amount

    def aim_at(self, target_pos: tuple[int, int]):
        center = self.get_center()
        self.target_angle = math.degrees(math.atan2(target_pos[1] - center[1], target_pos[0] - center[0]))

class Fire:
    def __init__(self, screen: pygame.Surface, parent_turret: Turret, image: pygame.Surface, size: int = -1):
        self.screen = screen
        self.turret = parent_turret
        self.image = image
        self.size = size

    def draw(self):
        barrel = self.turret.get_barrel()
        rotated = pygame.transform.rotate(self.image, self.turret.get_angle())
        centered_rect = rotated.get_rect(center=(barrel[0], barrel[1]))
        self.screen.blit(rotated, centered_rect)

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

    def get_cell(self, index: int) -> Cell:
        pos = self.index_to_rect(index)
        return self.grid[pos[0]][pos[1]]

    def get_rows(self):
        return self.screen.get_width() // self.size

    def draw(self):
        n = self.get_rows()
        for x in range(0, n):
            for y in range(0, n):
                rect = (x * self.size, y * self.size, self.size, self.size)
                self.grid[x][y].draw(rect)

                i = y + x * n
                text = font.render(f"{self.grid[x][y].value}", True, (0, 0, 0))
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

    def neighbors(self, pos: tuple[int, int]) -> tuple[int, int, int, int]:
        x = pos[0]
        y = pos[1]
        left = -1 if x - 1 < 0 else x - 1
        right = -1 if x + 1 >= self.get_rows() else x + 1
        up = -1 if y - 1 < 0 else x - 1
        down = -1 if y + 1 > self.get_rows() else y + 1
        return left, right, up, down

    def flood_fill(self, start: int, end: int):
        starting_cell = self.get_cell(start)
        starting_cell.value = 0
        cells: list[Cell] = [starting_cell]
        next_cells: list[Cell] = []
        run = True
        while run:
            for cell in cells:
                neighbors = self.neighbors(self.index_to_rect(cell.index))
                for neighbor_index in neighbors:
                    if neighbor_index == -1:
                        continue
                    neighbor = self.get_cell(neighbor_index)
                    if neighbor.state != State.BLOCKED and neighbor.value == -1:
                        neighbor.value = cell.value + 1
                        next_cells.append(neighbor)
                        if neighbor.index == end:
                            run = False
                            break
                if not run:
                    break













class Game:
    """Handles the gameplay, delegation, and processes most events"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.game_active = True
        self.map = Map(screen)
        self.tanks: list[Tank] = []

        self.tanks.append(Tank(screen, (200, 200), pygame.image.load("../images/Tank_Base.png"),
                               pygame.image.load("../images/Tank_Turret.png")))

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
            # pos = self.map.mouse_to_rect(event.pos)
            # self.map.grid[pos[0]][pos[1]].highlighted = True
            # self.tanks[0].move_to((random.randint(100, 300), random.randint(100, 300)))
            # self.tanks[0].shoot()

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

        # self.tanks[0].turret.aim_at(pygame.mouse.get_pos())

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
