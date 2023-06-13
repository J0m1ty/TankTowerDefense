from util import *
import pygame
import random
import sys
import math

# Global variables
pygame.font.init()
state_manager = None
font = pygame.font.SysFont("avenir", 16)
click = False
keys = []


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

    def __str__(self):
        return self.index


class Game:
    """Handles the gameplay, delegation, and processes most events"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.game_active = True
        self.map = Map(screen)
        self.tanks: list[Tank] = []

    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass

        if keys[pygame.K_SPACE]:
            self.tanks.append(Tank(self.screen, self, (random.randrange(100, 300), random.randrange(100, 300)),
                                   pygame.image.load("../images/Tank_Base.png"),
                                   pygame.image.load("../images/Tank_Turret.png")))

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            cell = self.map.get_cell(self.map.pos_to_index(pygame.mouse.get_pos()))
            if cell is not None:
                cell.highlighted = True
                cell.state = State.BLOCKED
                self.map.flood_fill(0, 399)

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
            # tank.turret.aim_at(pygame.mouse.get_pos())
            # if keys[pygame.K_RIGHT]:
            #     tank.rotate_by(2)
            # if keys[pygame.K_LEFT]:
            #     tank.rotate_by(-2)

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.map.draw()

        for tank in self.tanks:
            tank.draw()


class Tank:
    def __init__(self, screen: pygame.Surface, game: Game, pos: tuple[int, int], base_image: pygame.Surface,
                 turret_image: pygame.Surface, speed: float = 1, rot_speed: float = 2, turret_rot_speed: float = 3,
                 angle: float = 0, size: int = 32):
        self.screen = screen
        self.game = game
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
        self.target_pos = self.get_center()
        self.rot_speed = rot_speed
        self.target_angle = self.angle
        self.auto = True

    def get_angle(self):
        return 90 - self.angle

    def get_center(self):
        return self.pos[0] - self.size / 2, self.pos[1] - self.size / 2

    def shoot(self):
        self.projectiles.append(Projectile(self.screen, self, 10, 2))
        self.fire_timer = 8

    def closest_cell(self) -> Cell:
        return self.game.map.get_cell(self.game.map.pos_to_index(self.get_center()))

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

                    if self.auto:
                        cell = self.closest_cell()
                        path = self.game.map.traverse(cell.index, 399, 1)
                        if len(path) > 1:
                            pos = self.game.map.rect_to_pos(self.game.map.index_to_rect(path[1].index))
                            self.move_to((pos[0] + self.game.map.size / 2, pos[1] + self.game.map.size / 2))
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
        self.idle = True
        self.turret_rot_speed = turret_rot_speed
        self.target_angle = 0

    def get_size(self) -> int:
        return self.tank.size if self.size == -1 else self.size

    def get_angle(self) -> float:
        return self.tank.get_angle() - self.angle_offset - 90

    def get_center(self) -> tuple[float, float]:
        size = self.get_size()
        return (self.tank.pos[0] + self.pos_offset[0]) - size / 2, (self.tank.pos[1] + self.pos_offset[1]) - size / 2

    def get_barrel(self) -> tuple[float, float]:
        center = self.get_center()
        return center[0] + (self.tank.size / 2) * math.cos(math.radians(-90 - self.get_angle())), center[1] + (
                self.tank.size / 2) * math.sin(math.radians(-90 - self.get_angle()))

    def update(self):
        if self.idle:
            self.target_angle = 90 - self.tank.get_angle()

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

        self.flood_fill(0, 399)

    def reset_values(self):
        n = self.get_rows()
        for x in range(0, n):
            for y in range(0, n):
                self.grid[x][y].value = -1

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
                cell = self.grid[x][y]
                cell.draw(rect)

                text = font.render(f"{cell.value}", True, (0, 0, 0))
                text_rect = text.get_rect(center=(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2))
                self.screen.blit(text, text_rect)

    def pos_to_rect(self, pos: tuple[int, int]) -> tuple[int, int]:
        x = pos[0]
        y = pos[1]
        return x // self.size, y // self.size

    def rect_to_index(self, rect: tuple[int, int]) -> int:
        return rect[0] * self.get_rows() + rect[1]

    def pos_to_index(self, pos: tuple[float, float]) -> int:
        return self.rect_to_index(self.pos_to_rect((int(pos[0]), int(pos[1]))))

    def index_to_rect(self, index: int) -> tuple[int, int]:
        return int(index // self.get_rows()), int(index % self.get_rows())

    def rect_to_pos(self, pos: tuple[int, int]) -> tuple[int, int]:
        x = math.floor(pos[0] * self.size)
        y = math.floor(pos[1] * self.size)
        return x, y

    def neighbors(self, pos: tuple[int, int]) -> list[int, int, int, int]:
        x = pos[0]
        y = pos[1]
        return [None if x - 1 < 0 else self.rect_to_index((x - 1, y)),
                None if x + 1 >= self.get_rows() else self.rect_to_index((x + 1, y)),
                None if y - 1 < 0 else self.rect_to_index((x, y - 1)),
                None if y + 1 >= self.get_rows() else self.rect_to_index((x, y + 1))]

    def flood_fill(self, start: int, end: int):
        self.reset_values()

        ending_cell = self.get_cell(end)
        ending_cell.value = 0
        cells: list[Cell] = [ending_cell]
        next_cells: list[Cell] = []
        while True:
            for cell in cells:
                neighbors = self.neighbors(self.index_to_rect(cell.index))
                for neighbor_index in neighbors:
                    if neighbor_index is None:
                        continue
                    neighbor = self.get_cell(neighbor_index)
                    if neighbor.state != State.BLOCKED and neighbor.value == -1:
                        neighbor.value = cell.value + 1
                        next_cells.append(neighbor)
            if len(next_cells) == 0:
                break
            else:
                cells = next_cells
                next_cells = []

    def traverse(self, start: int, end: int, max_range: int = -1) -> list[Cell]:
        start_cell = self.get_cell(start)
        end_cell = self.get_cell(end)
        path: list[Cell] = [start_cell]
        while True:
            cell = path[len(path) - 1]
            valid: list[Cell] = []
            neighbors = self.neighbors(self.index_to_rect(cell.index))
            for neighbor_index in neighbors:
                if neighbor_index is None:
                    continue
                neighbor = self.get_cell(neighbor_index)
                if neighbor.state == State.OPEN and neighbor.value < cell.value:
                    valid.append(neighbor)

            if len(valid) == 0:
                return []

            closest_neighbor = valid[random.randrange(len(valid))]
            best_dist = math.inf
            for neighbor in valid:
                pos1 = self.index_to_rect(neighbor.index)
                pos2 = self.index_to_rect(end_cell.index)
                dist = math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2)
                if dist < best_dist:
                    best_dist = dist
                    closest_neighbor = neighbor

            path.append(closest_neighbor)

            if closest_neighbor is None or closest_neighbor.index == end or (
                    max_range != -1 and closest_neighbor.value == max_range):
                return path


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
