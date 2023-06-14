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


class TeamImage:
    def __init__(self, team: Team, url: str):
        self.team = team
        self.url = url


class TankBase:
    def __init__(self, name: str, images: list[TeamImage], health: int,
                 speed: int, rotation_speed: int, cost: int):
        self.name = name
        self.images = images
        self.health = health
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.cost = cost


class TankTurret:
    def __init__(self, name: str, images: list[TeamImage], damage: int, fire_rate: int,
                 rotation_speed: int, range: int, cost: int):
        self.name = name
        self.images = images
        self.damage = damage
        self.fire_rate = fire_rate
        self.rotation_speed = rotation_speed
        self.range = range
        self.cost = cost


class TankData:
    def __init__(self, tank_base: TankBase, tank_turret: TankTurret):
        self.tank_base = tank_base
        self.tank_turret = tank_turret


tank_bases = [
    TankBase("Car", [TeamImage(Team.RED, "../images/Red_Car_Base.PNG"),
                     TeamImage(Team.GREEN, "../images/Car_Base.PNG")], 100, 100 // 60, 3, 100),
    TankBase("Tracks", [TeamImage(Team.RED, "../images/Red_Tank_Base.PNG"),
                        TeamImage(Team.GREEN, "../images/Tank_Base.PNG")], 200, 70 // 60, 1, 200),
    # TankBase("Hover",  [TeamImage(Team.RED, "../images/.PNG"), TeamImage(Team.GREEN, "../images/.PNG")], 150, 85 / 50, 400)
]

tank_turrets = [
    TankTurret("Single", [TeamImage(Team.RED, "../images/Red_Tank_Turret.PNG"),
                          TeamImage(Team.GREEN, "../images/Tank_Turret.PNG")], 15, 60, 2, 200, 100),
    TankTurret("Double", [TeamImage(Team.RED, "../images/Red_Tank_Double_Turret.PNG"),
                          TeamImage(Team.GREEN, "../images/Tank_Double_Turret.PNG")], 15, 120, 3, 200, 200)
    # TankTurret("Rocket", [TeamImage(Team.RED, "../images/.PNG"), TeamImage(Team.GREEN, "../images/.PNG")], 100, 30, 3, 400, 200)
]


class Cell:
    """A unit of the map, used for holding towers and pathfinding"""

    def __init__(self, screen, index):
        self.index = index
        self.state = State.OPEN
        self.highlighted = False
        self.screen = screen
        self.value = [-1, -1, -1]
        self.linked_tanks: list[Tank] = []
        self.linked_base: Base | None = None
        self.linked_tower = None

        teams = [team.value for team in Team]

        for team in teams:
            self.value[team] = -1

    def draw(self, rect):
        color = (20, 20, 20, 20)
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
        self.bases: list[Base] = []
        self.map = Map(screen, self)

        self.bases.append(
            Base(screen, pygame.image.load("../images/Base.png"), self, self.map.get_cell(83), self.map.get_cell(144),
                 Team.GREEN))

        self.bases.append(
            Base(screen, pygame.image.load("../images/Red_Base.png"), self, self.map.get_cell(316),
                 self.map.get_cell(255),
                 Team.RED))

        self.flood_fill()

    def get_event(self, event):
        pass

    def update(self):
        if pygame.mouse.get_pressed()[0]:
            cell = self.map.get_cell(self.map.pos_to_index(pygame.mouse.get_pos()))
            if cell is not None:
                cell.highlighted = True
                cell.state = State.BLOCKED
                self.flood_fill()

        for base in self.bases:
            base.update()

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.map.draw()

        for base in self.bases:
            base.draw()

    def flood_fill(self):
        self.map.reset_values()
        for base in self.bases:
            base.flood_fill()


class Base:
    def __init__(self, screen: pygame.Surface, image: pygame.Surface, game: Game, base_cell: Cell, spawn_cell: Cell,
                 team: Team):
        self.screen = screen
        self.base_image = image
        self.game = game
        self.base_cell = base_cell
        self.spawn_cell = spawn_cell
        self.team = team
        self.tanks = []

        base_cell_pos = self.game.map.index_to_rect(self.base_cell.index)
        for x in range(-2, 3):
            for y in range(-1, 2):
                cell = game.map.get_cell(game.map.rect_to_index((base_cell_pos[0] + x, base_cell_pos[1] + y)))
                cell.state = State.BLOCKED
                cell.linked_base = self

        self.spawn_timer = 0
        self.spawn_delay = 120

    def spawn(self, upgrades: tuple[int, int]):
        tank_data = TankData(tank_bases[upgrades[0]], tank_turrets[upgrades[1]])
        pos = self.game.map.rect_to_pos(self.game.map.index_to_rect(self.spawn_cell.index))
        pos = (pos[0] + self.game.map.size, pos[1] + self.game.map.size)
        self.tanks.append(Tank(self.screen, self, pos, tank_data))

    def other_base(self):
        other_bases = filter(lambda b: b.team != self.team, self.game.bases)

        for base in other_bases:
            return base

    def flood_fill(self):
        self.game.map.flood_fill(self.spawn_cell.index, self.other_base().base_cell.index, self.team)

    def update(self):
        if self.spawn_timer <= 0:
            self.spawn_timer = self.spawn_delay
            self.spawn((0, 0))
        else:
            self.spawn_timer -= 1

        for tank in self.tanks:
            tank.update()
            if tank.health <= 0:
                cell = tank.closest_cell
                if cell is not None:
                    cell.linked_tanks.remove(tank)
                self.tanks.remove(tank)

    def draw(self):
        base_cell_pos = self.game.map.index_to_rect(self.base_cell.index)
        base_cell_offset = self.game.map.get_cell(self.game.map.rect_to_index((base_cell_pos[0] - 2, base_cell_pos[1] - 1)))

        pos = self.game.map.rect_to_pos(self.game.map.index_to_rect(base_cell_offset.index))
        self.screen.blit(self.base_image, pos)

        for tank in self.tanks:
            tank.draw()


class Tank:
    def __init__(self, screen: pygame.Surface, base: Base, pos: tuple[int, int],
                 data: TankData, angle: float = 0, size: int = 32):

        self.screen = screen
        self.base = base
        self.image = pygame.image.load(
            list(filter(lambda image: image.team == base.team, data.tank_base.images))[0].url)
        self.pos = pos
        self.data = data.tank_base
        self.angle = angle
        self.size = size
        self.turret = Turret(screen, self, data.tank_turret)
        self.projectiles: list[Projectile] = []
        self.fire_timer = 0
        self.closest_cell: Cell | None = None
        self.health = data.tank_base.health

        # Targeting
        self.moving = True
        self.target_pos = self.get_center()
        self.target_angle = self.angle
        self.auto = True

    def damage(self, amount: int):
        self.health -= amount

    def bounding_box(self) -> pygame.Rect:
        return pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)

    def get_angle(self):
        return 90 - self.angle

    def get_center(self):
        return self.pos[0] - self.size / 2, self.pos[1] - self.size / 2

    def shoot(self):
        if self.fire_timer <= 0:
            self.projectiles.append(Projectile(self.screen, self, 10, 2))
            self.fire_timer = 8

    def get_closest_cell(self) -> Cell:
        cell = self.base.game.map.get_cell(self.base.game.map.pos_to_index(self.get_center()))

        if self.closest_cell is not None:
            self.closest_cell.linked_tanks.remove(self)

        self.closest_cell = cell

        cell.linked_tanks.append(self)

        return cell

    def update(self):
        self.get_closest_cell()

        self.get_closest_target()

        if self.moving:
            sin = math.sin(math.radians(self.target_angle - self.angle))
            targeted = round(sin * 20) / 20 == 0
            if targeted:
                self.rotate_instant(self.target_angle)

                center = self.get_center()
                dist = math.sqrt(
                    math.pow(center[0] - self.target_pos[0], 2) + math.pow(center[1] - self.target_pos[1], 2))
                close = equals(0, dist, self.data.speed * 1.1)
                if close:
                    self.move_instant((self.target_pos[0] + self.size / 2, self.target_pos[1] + self.size / 2))

                    if self.auto:
                        path = self.base.game.map.traverse(self.closest_cell.index,
                                                           self.base.other_base().base_cell.index,
                                                           self.base.team, 1)
                        if len(path) > 1:
                            pos = self.base.game.map.rect_to_pos(self.base.game.map.index_to_rect(path[1].index))
                            self.move_to((pos[0] + self.base.game.map.size / 2, pos[1] + self.base.game.map.size / 2))
                else:
                    self.move_by(self.data.speed)
            else:
                amount = abs(sin) / sin * self.data.rotation_speed
                self.rotate_by(amount)

        self.turret.update()

        for projectile in self.projectiles:
            projectile.update()
            if projectile.die:
                self.projectiles.remove(projectile)

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

    def get_closest_target(self):
        other_tanks = self.base.other_base().tanks
        closest_tank: Tank | None = None
        closest_dist = math.inf
        for tank in other_tanks:
            pos1 = tank.get_center()
            pos2 = self.get_center()
            dist = math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2)
            if dist < closest_dist:
                closest_dist = dist
                closest_tank = tank

        if closest_tank is not None and closest_dist <= math.pow(self.turret.data.range, 2):
            self.turret.idle = False
            self.turret.aim_at(tuple[int, int](closest_tank.get_center()))
            self.shoot()
        else:
            self.turret.idle = True


class Turret:
    def __init__(self, screen: pygame.Surface, parent_tank: Tank, data: TankTurret, angle: float = 0, size: int = -1):
        self.screen = screen
        self.tank = parent_tank
        self.fire = Fire(screen, self, pygame.image.load("../images/Fire.png"))
        self.data = data
        self.image = pygame.image.load(
            list(filter(lambda image: image.team == parent_tank.base.team, data.images))[0].url)
        self.pos_offset = (0, 0)
        self.angle_offset = angle
        self.size = size

        # Targeting
        self.idle = True
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
            amount = abs(sin) / sin * self.data.rotation_speed
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
        self.init_pos = self.pos
        self.angle = tank.turret.get_angle()
        self.speed = speed
        self.size = size
        self.die = False

    def draw(self):
        pygame.draw.circle(self.screen, (2, 2, 2), self.pos, self.size)

    def update(self):
        x = self.pos[0] + self.speed * math.cos(math.radians(-90 - self.angle))
        y = self.pos[1] + self.speed * math.sin(math.radians(-90 - self.angle))
        self.pos = (x, y)
        dist = math.pow(x - self.init_pos[0], 2) + math.pow(y - self.init_pos[1], 2)
        if dist > math.pow(self.tank.turret.data.range, 2):
            self.die = True
        else:
            self.collide()

    def collide(self):
        game_map = self.tank.base.game.map
        if not game_map.pos_in_map(self.pos):
            self.die = True
            return
        center_cell = game_map.pos_to_index(self.pos)
        neighbors = game_map.neighbors(game_map.index_to_rect(center_cell), True)
        total = [game_map.get_cell(center_cell)]
        for neighbor in neighbors:
            if neighbor is not None:
                total.append(game_map.get_cell(neighbor))
        close_tanks: list[Tank] = []
        for cell in total:
            close_tanks.extend(cell.linked_tanks)
        for tank in close_tanks:
            if tank.base.team == self.tank.base.team:
                continue
            bounding_box = tank.bounding_box()
            hit = bounding_box.collidepoint(self.pos[0], self.pos[1])
            if hit:
                self.die = True
                tank.damage(self.tank.turret.data.damage)
                break


class Map:
    """Contains the list of cells in the grid and performs algorithms on them"""

    def __init__(self, screen: pygame.Surface, game: Game, size: int = 32):
        self.screen = screen
        self.game = game
        self.size = size
        self.grid: list[list[Cell]] = []

        n = self.get_rows()
        for x in range(0, n):
            self.grid.append([])
            for y in range(0, n):
                self.grid[x].append(Cell(self.screen, self.rect_to_index((x, y))))

    def reset_values(self):
        teams = [team.value for team in Team]

        n = self.get_rows()
        for x in range(0, n):
            for y in range(0, n):
                for team in teams:
                    self.grid[x][y].value[team] = -1

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

                # text = font.render(f"{cell.value[Team.RED.value]}", True, (0, 0, 0))
                # text_rect = text.get_rect(center=(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2))
                # self.screen.blit(text, text_rect)

    def pos_to_rect(self, pos: tuple[float, float]) -> tuple[int, int]:
        return int(pos[0] // self.size), int(pos[1] // self.size)

    def pos_in_map(self, pos: tuple[float, float]) -> bool:
        rect = self.pos_to_rect(pos)
        return rect[0] >= 0 and rect[0] < self.get_rows() and rect[1] >= 0 and rect[1] < self.get_rows()

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

    def neighbors(self, pos: tuple[int, int], include_diagonals: bool = False) -> list[int, int, int, int]:
        x = pos[0]
        y = pos[1]
        out = [None if x - 1 < 0 else self.rect_to_index((x - 1, y)),
               None if x + 1 >= self.get_rows() else self.rect_to_index((x + 1, y)),
               None if y - 1 < 0 else self.rect_to_index((x, y - 1)),
               None if y + 1 >= self.get_rows() else self.rect_to_index((x, y + 1))]
        if include_diagonals:
            out.extend([
                None if x - 1 < 0 or y - 1 < 0 else self.rect_to_index((x - 1, y - 1)),
                None if x + 1 >= self.get_rows() or y - 1 < 0 else self.rect_to_index((x + 1, y - 1)),
                None if x + 1 >= self.get_rows() or y + 1 >= self.get_rows() else self.rect_to_index((x + 1, y + 1)),
                None if x - 1 < 0 or y + 1 >= self.get_rows() else self.rect_to_index((x - 1, y + 1)),
            ])
        return out

    def flood_fill(self, start: int, end: int, team: Team):
        team = team.value

        ending_cell = self.get_cell(end)
        end_cell_blocked = ending_cell.state != State.OPEN
        if not end_cell_blocked:
            ending_cell.value[team] = 0
        cells: list[Cell] = [ending_cell]
        next_cells: list[Cell] = []
        while True:
            for cell in cells:
                neighbors = self.neighbors(self.index_to_rect(cell.index))
                for neighbor_index in neighbors:
                    if neighbor_index is None:
                        continue
                    neighbor = self.get_cell(neighbor_index)
                    if neighbor.state == State.OPEN and neighbor.value[team] == -1:
                        neighbor.value[team] = cell.value[team] + 1
                        next_cells.append(neighbor)
                        end_cell_blocked = False
                    elif end_cell_blocked:
                        next_cells.append(neighbor)
            if len(next_cells) == 0:
                break
            else:
                cells = next_cells
                next_cells = []

    def traverse(self, start: int, end: int, team: Team, max_range: int = -1) -> list[Cell]:
        team = team.value

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
                if neighbor.state == State.OPEN and neighbor.value[team] < cell.value[team]:
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
                    max_range != -1 and closest_neighbor.value[team] == max_range):
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
