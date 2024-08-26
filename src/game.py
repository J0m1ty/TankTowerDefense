from util import *
import pygame
import random
import sys
import math

# Global variables
pygame.font.init()
font = pygame.font.SysFont("avenir", 38)
small_font = pygame.font.SysFont("avenir", 16)
medium_font = pygame.font.SysFont("avenir", 26)
click = False
keys = []
clock = pygame.time.Clock()

cell_states = [[2, 2, 2, 2, 2, 2, 0, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
               [2, 2, 2, 2, 0, 0, 0, 2, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
               [2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 1, 0, 2, 0, 2, 2, 0, 2, 2, 2],
               [2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
               [2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
               [2, 2, 2, 2, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2],
               [2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2],
               [2, 0, 0, 0, 0, 2, 2, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2],
               [2, 0, 0, 0, 0, 2, 2, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2],
               [2, 0, 0, 0, 0, 0, 0, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2],
               [2, 0, 0, 0, 0, 0, 0, 1, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 2, 2],
               [2, 0, 0, 0, 0, 0, 2, 1, 2, 1, 2, 2, 0, 0, 0, 0, 0, 0, 2, 2],
               [2, 0, 0, 0, 0, 0, 2, 1, 1, 1, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2],
               [2, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2],
               [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2],
               [1, 1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2],
               [1, 1, 1, 2, 2, 2, 1, 1, 0, 0, 0, 0, 0, 2, 0, 2, 2, 2, 2, 2],
               [1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
               [1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
               [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]


class TeamImage:
    def __init__(self, team: Team, url: str):
        self.team = team
        self.url = url


class TankBase:
    def __init__(self, name: str, images: list[TeamImage], health: int,
                 speed: int, rotation_speed: int, cost: int, hover: bool,
                 unlock_price: int, display: bool = True):
        self.name = name
        self.images = images
        self.health = health
        self.speed = speed
        self.rotation_speed = rotation_speed
        self.cost = cost
        self.hover = hover
        self.unlock_price = unlock_price
        self.display = display


class TankTurret:
    def __init__(self, name: str, images: list[TeamImage], damage: int, fire_cooldown: int,
                 rotation_speed: int, range: int, cost: int, barrels: list[tuple[float, float]],
                 unlock_price: int, display: bool = True, projectile_image: None | str = None):
        self.name = name
        self.images = images
        self.damage = damage
        self.fire_cooldown = fire_cooldown
        self.rotation_speed = rotation_speed
        self.range = range
        self.cost = cost
        self.projectile_image = projectile_image
        self.barrels = barrels
        self.unlock_price = unlock_price
        self.display = display


class TankData:
    def __init__(self, tank_base: TankBase, tank_turret: TankTurret):
        self.tank_base = tank_base
        self.tank_turret = tank_turret


tank_bases = [
    TankBase("Car", [TeamImage(Team.RED, "../images/Red_Car_Base.PNG"),
                     TeamImage(Team.GREEN, "../images/Car_Base.PNG")], 100, 100 // 80, 3, 100, False, 0),
    TankBase("Tracks", [TeamImage(Team.RED, "../images/Red_Tank_Base.PNG"),
                        TeamImage(Team.GREEN, "../images/Tank_Base.PNG")], 200, 70 // 70, 1, 200, False, 300),
    TankBase("Hover", [TeamImage(Team.RED, "../images/Red_Hover_Base.PNG"),
                       TeamImage(Team.GREEN, "../images/Hover_Base.PNG")], 150, 85 // 80, 2, 400, True, 600),
]

tank_turrets = [
    TankTurret("Single", [TeamImage(Team.RED, "../images/Red_Tank_Turret.PNG"),
                          TeamImage(Team.GREEN, "../images/Tank_Turret.PNG")], 15, 60, 2, 200, 100, [(0, 0)], 0),
    TankTurret("Double", [TeamImage(Team.RED, "../images/Red_Tank_Double_Turret.PNG"),
                          TeamImage(Team.GREEN, "../images/Tank_Double_Turret.PNG")], 15, 30, 3, 150, 200,
               [(-3, 0), (3, 0)], 300),
    TankTurret("Rocket", [TeamImage(Team.RED, "../images/Red_Tank_Rocket_Turret.PNG"),
                          TeamImage(Team.GREEN, "../images/Tank_Rocket_Turret.PNG")], 100, 180, 3, 200, 400, [], 600,
               True,
               "../images/Rocket.png")
]

towers = [
    TankData(
        TankBase("Stationary", [], 50, 0, 0, 0, False, False),
        TankTurret("Sandbags", [TeamImage(Team.RED, "../images/Red_Sandbag.png"),
                                TeamImage(Team.GREEN, "../images/Sandbag.png")], 0, 0, 0, 0, 15, [], 0),
    ),
    TankData(
        TankBase("Stationary", [], 100, 0, 0, 0, False, False),
        TankTurret("Hedgehog", [TeamImage(Team.RED, "../images/Red_Hedgehog.png"),
                                TeamImage(Team.GREEN, "../images/Hedgehog.png")], 0, 0, 0, 0, 30, [], 45),
    ),
    TankData(
        TankBase("Stationary", [], 400, 0, 0, 0, False, False),
        TankTurret("Howitzer", [TeamImage(Team.RED, "../images/Red_Howitzer.png"),
                                TeamImage(Team.GREEN, "../images/Howitzer.png")], 75, 60, 1, 90, 100, [], 200),
    ),
]


class Cell:
    """A unit of the map, used for holding towers and pathfinding"""

    def __init__(self, screen, index):
        self.index = index
        self.state = State.OPEN
        self.highlighted = False
        self.screen = screen
        self.value = []
        self.linked_tanks: list[Tank] = []
        self.linked_base: Base | None = None
        self.linked_tower: Tank | None = None

        teams = [team.value for team in Team]

        for team in teams:
            self.value.append(-1)

    def draw(self, rect: tuple[int, int, int, int], s: pygame.Surface):
        color = (20, 20, 20)
        if self.highlighted:
            color = (255, 0, 0)
            if self.state == State.WATER:
                color = (0, 0, 255)
        pygame.draw.rect(s, color, rect, 1)

    def __str__(self):
        return self.index


class Game:
    """Handles the gameplay, delegation, and processes most events"""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.size = 640
        self.game_active = True
        self.bases: list[Base] = []
        self.map = Map(screen, self)
        self.selected_base = 0
        self.selected_turret = 0
        self.selected_tower = 0
        self.player_team = Team.GREEN

        self.unlocked_bases: list[bool] = []
        for base in tank_bases:
            self.unlocked_bases.append(True if base.unlock_price == 0 else False)

        self.unlocked_turrets: list[bool] = []
        for turret in tank_turrets:
            self.unlocked_turrets.append(True if turret.unlock_price == 0 else False)

        self.unlocked_towers: list[bool] = []
        for tower in towers:
            self.unlocked_towers.append(True if tower.tank_turret.unlock_price == 0 else False)

        self.menu_image = pygame.image.load("../images/Menu.png")
        self.selection = pygame.image.load("../images/Selector.png")
        self.cover = pygame.image.load("../images/Research_Cover.png")

        self.placing_tower = False
        self.immune = False

        self.error_message = ""
        self.error_timer = 0

        self.buy_timer = 3

        self.bases.append(
            Base(screen, pygame.image.load("../images/Base.png"),
                 pygame.image.load("../images/Base_Shadow.png"), self, self.map.get_cell(62), self.map.get_cell(123),
                 Team.GREEN, Team.GREEN_WATER))

        self.bases.append(
            Base(screen, pygame.image.load("../images/Red_Base.png"),
                 pygame.image.load("../images/Base_Shadow.png"), self, self.map.get_cell(316),
                 self.map.get_cell(255),
                 Team.RED, Team.RED_WATER))

        self.flood_fill()

    def get_event(self, event):
        pass

    def update(self):
        if click and not self.immune and self.placing_tower:
            pos = pygame.mouse.get_pos()
            player_base = list(filter(lambda b: b.team == self.player_team, self.bases))[0]

            closest_dist = math.inf
            base_cells = player_base.base_cells()
            for cell in base_cells:
                cell_pos = self.map.rect_to_pos(self.map.index_to_rect(cell.index))
                cell_center = (cell_pos[0] + self.map.size / 2, cell_pos[1] + self.map.size / 2)
                dist = 0.66 * math.pow(cell_center[0] - pos[0], 2) + math.pow(cell_center[1] - pos[1], 2) * 1.5
                if closest_dist > math.pow(dist, 2):
                    closest_dist = dist

            if self.map.pos_in_map(pos) and closest_dist < math.pow(self.size / 1.4142, 2):
                cell = self.map.get_cell(self.map.pos_to_index(pos))

                if cell is not None and player_base.money >= towers[self.selected_tower].tank_turret.cost:
                    success = player_base.add_tower(self.selected_tower, cell.index)
                    if success:
                        self.flood_fill()
                        player_base.money -= towers[self.selected_tower].tank_turret.cost
                        self.placing_tower = False
                    else:
                        self.placing_tower = False
                        self.error_timer = 2
                        self.error_message = "Invalid position"
                else:
                    self.placing_tower = False
                    if not player_base.money >= towers[self.selected_tower].tank_turret.cost:
                        self.error_timer = 2
                        self.error_message = "Insufficient funds"
            else:
                self.placing_tower = False

        for base in self.bases:
            base.update()

        self.immune = False

        if self.buy_timer > 0:
            self.buy_timer -= 1 / clock.get_fps()
        else:
            enemy_base = list(filter(lambda base: base.team != self.player_team, self.bases))[0]
            tries = 20
            while tries > 0:
                tvt = random.randint(0,300)
                if tvt > 50:
                    tank_base = random.randint(0, 2)
                    tank_top = random.randint(0, 2)
                    cost = tank_bases[tank_base].cost + tank_turrets[tank_top].cost
                    if enemy_base.money >= cost and (self.unlocked_bases[tank_base] and self.unlocked_turrets[tank_top]):
                        enemy_base.money -= cost
                        enemy_base.spawn((tank_base, tank_top))
                        if enemy_base.money < 500:
                            self.buy_timer = random.randint(4, 8)
                        else:
                            self.buy_timer = random.randint(2, 4)
                        tries = 0
                else:
                    tower = random.randint(0, 2)
                    cost = towers[tower].tank_turret.cost
                    if enemy_base.money >= cost and self.unlocked_towers[tower]:
                        placing = 100
                        while placing > 0:
                            try_cell_index = random.randint(0, self.map.get_rows() * self.map.get_rows() - 1)
                            try_cell_pos = self.map.rect_to_pos(self.map.index_to_rect(try_cell_index))
                            try_cell_pos_center = (try_cell_pos[0] + self.map.size / 2, try_cell_pos[1] + self.map.size / 2)

                            enemy_base = list(filter(lambda base: base.team != self.player_team, self.bases))[0]

                            closest_dist = math.inf
                            base_cells = enemy_base.base_cells()
                            for cell in base_cells:
                                cell_pos = self.map.rect_to_pos(self.map.index_to_rect(cell.index))
                                cell_center = (cell_pos[0] + self.map.size / 2, cell_pos[1] + self.map.size / 2)
                                dist = 0.66 * math.pow(cell_center[0] - try_cell_pos_center[0], 2) + math.pow(cell_center[1] - try_cell_pos_center[1],
                                                                                              2) * 1.5
                                if closest_dist > math.pow(dist, 2):
                                    closest_dist = dist

                            if closest_dist < math.pow(self.size / 1.4142, 2):
                                success = enemy_base.add_tower(tower, try_cell_index)
                                if success:
                                    enemy_base.money -= cost
                                    self.flood_fill()
                                    self.buy_timer = random.randint(5, 9)
                                    tries = 0
                                    break
                            placing -= 1
                tries -= 1
                self.buy_timer = random.randint(2, 8)


    def draw(self):
        self.map.draw()

        for base in self.bases:
            base.draw()

        self.buy_menu()

        if self.placing_tower:
            image = pygame.image.load(list(filter(lambda tower : tower.team == self.player_team, towers[self.selected_tower].tank_turret.images))[0].url)
            centered_rect = image.get_rect(center=(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]))
            self.screen.blit(image, centered_rect)

    def flood_fill(self) -> bool:
        self.map.reset_values()
        success = True
        for base in self.bases:
            result = base.flood_fill()
            if not result:
                success = False
        return success

    def buy_button(self, x, y, unlocked_list: list[bool], index: int,
                   selected_index: int, cost: int, price: int, name: str):
        button_container = pygame.Rect(x, y, 729 - 651, 133 - 82)

        if not unlocked_list[index]:
            price_text = small_font.render(f"{price}", True, (254, 254, 254))
            self.screen.blit(price_text, (x + 54, y + 38.5))
        else:
            self.screen.blit(self.cover, (x + 4, y + 39))

        if selected_index == index:
            self.screen.blit(self.selection, (x - 8, y - 7))

        name_text = medium_font.render(f"{name}", True, (200, 255, 220))
        self.screen.blit(name_text, (button_container.centerx - name_text.get_width() / 2, button_container.centery - name_text.get_height() / 2 - 9))

        cost_text = small_font.render(f"{cost}", True, (254, 254, 254))
        self.screen.blit(cost_text, (x + 32.5, y + 27.5))

        return click and button_container.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])




    def buy_menu(self):
        buy_container = pygame.Rect(self.size, 0, self.screen.get_width() - self.size, self.size)
        self.screen.blit(self.menu_image, buy_container)

        player_base = list(filter(lambda base: base.team == self.player_team, self.bases))[0]
        player_money = small_font.render(f"{player_base.money}", True, (252, 252, 252))
        self.screen.blit(player_money, (695, 318.5 + player_money.get_height() // 2))
        player_health = small_font.render(f"{player_base.health}", True, (252, 252, 252))
        self.screen.blit(player_health, (695, 382.5 + player_health.get_height() // 2))

        if self.buy_button(651, 82, self.unlocked_bases, 0, self.selected_base, tank_bases[0].cost, tank_bases[0].unlock_price, tank_bases[0].name):
            if self.selected_base != 0 and self.unlocked_bases[0]:
                self.selected_base = 0
            elif not self.unlocked_bases[0]:
                if player_base.money >= tank_bases[0].unlock_price:
                    player_base.money -= tank_bases[0].unlock_price
                    self.selected_base = 0
                    self.unlocked_bases[0] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(651, 146, self.unlocked_bases, 1, self.selected_base, tank_bases[1].cost,
                           tank_bases[1].unlock_price, tank_bases[1].name):
            if self.selected_base != 1 and self.unlocked_bases[1]:
                self.selected_base = 1
            elif not self.unlocked_bases[1]:
                if player_base.money >= tank_bases[1].unlock_price:
                    player_base.money -= tank_bases[1].unlock_price
                    self.selected_base = 1
                    self.unlocked_bases[1] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(651, 210, self.unlocked_bases, 2, self.selected_base, tank_bases[2].cost,
                           tank_bases[2].unlock_price, tank_bases[2].name):
            if self.selected_base != 2 and self.unlocked_bases[2]:
                self.selected_base = 2
            elif not self.unlocked_bases[2]:
                if player_base.money >= tank_bases[2].unlock_price:
                    player_base.money -= tank_bases[2].unlock_price
                    self.selected_base = 2
                    self.unlocked_bases[2] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(743, 82, self.unlocked_turrets, 0, self.selected_turret, tank_turrets[0].cost,
                           tank_turrets[0].unlock_price, tank_turrets[0].name):
            if self.selected_turret != 0 and self.unlocked_turrets[0]:
                self.selected_turret = 0
            elif not self.unlocked_turrets[0]:
                if player_base.money >= tank_turrets[0].unlock_price:
                    player_base.money -= tank_turrets[0].unlock_price
                    self.selected_turret = 0
                    self.unlocked_turrets[0] = True
                else:
                        self.error_timer = 2
                        self.error_message = "Insufficient funds"

        if self.buy_button(743, 146, self.unlocked_turrets, 1, self.selected_turret, tank_turrets[1].cost,
                           tank_turrets[1].unlock_price, tank_turrets[1].name):
            if self.selected_turret != 1 and self.unlocked_turrets[1]:
                self.selected_turret = 1
            elif not self.unlocked_turrets[1]:
                if player_base.money >= tank_turrets[1].unlock_price:
                    player_base.money -= tank_turrets[1].unlock_price
                    self.selected_turret = 1
                    self.unlocked_turrets[1] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(743, 210, self.unlocked_turrets, 2, self.selected_turret, tank_turrets[2].cost,
                           tank_turrets[2].unlock_price, tank_turrets[2].name):
            if self.selected_turret != 2 and self.unlocked_turrets[2]:
                self.selected_turret = 2
            elif not self.unlocked_turrets[2]:
                if player_base.money >= tank_turrets[2].unlock_price:
                    player_base.money -= tank_turrets[2].unlock_price
                    self.selected_turret = 2
                    self.unlocked_turrets[2] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(744, 304, self.unlocked_towers, 0, self.selected_tower, towers[0].tank_turret.cost,
                           towers[0].tank_turret.unlock_price, towers[0].tank_turret.name):
            if self.selected_tower != 0 and self.unlocked_towers[0]:
                self.selected_tower = 0
            elif not self.unlocked_towers[0]:
                if player_base.money >= towers[0].tank_turret.unlock_price:
                    player_base.money -= towers[0].tank_turret.unlock_price
                    self.selected_tower = 0
                    self.unlocked_towers[0] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(744, 146 - 82 + 304, self.unlocked_towers, 1, self.selected_tower,
                           towers[1].tank_turret.cost, towers[1].tank_turret.unlock_price, towers[1].tank_turret.name):
            if self.selected_tower != 1 and self.unlocked_towers[1]:
                self.selected_tower = 1
            elif not self.unlocked_towers[1]:
                if player_base.money >= towers[1].tank_turret.unlock_price:
                    player_base.money -= towers[1].tank_turret.unlock_price
                    self.selected_tower = 1
                    self.unlocked_towers[1] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        if self.buy_button(744, 210 - 82 + 304, self.unlocked_towers, 2, self.selected_tower,
                           towers[2].tank_turret.cost, towers[2].tank_turret.unlock_price, towers[2].tank_turret.name):
            if self.selected_tower != 2 and self.unlocked_towers[2]:
                self.selected_tower = 2
            elif not self.unlocked_towers[2]:
                if player_base.money >= towers[2].tank_turret.unlock_price:
                    player_base.money -= towers[2].tank_turret.unlock_price
                    self.selected_tower = 2
                    self.unlocked_towers[2] = True
                else:
                    self.error_timer = 2
                    self.error_message = "Insufficient funds"

        buy_tank_button = pygame.Rect(651, 432, 729 - 651, 25)
        if buy_tank_button.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and click:
            cost = tank_bases[self.selected_base].cost + tank_turrets[self.selected_turret].cost
            if player_base.money >= cost:
                player_base.money -= cost
                player_base.spawn((self.selected_base, self.selected_turret))
            else:
                self.error_timer = 2
                self.error_message = "Insufficient funds"

        buy_tower_button = pygame.Rect(651, 459, 729 - 651, 25)
        if buy_tower_button.collidepoint(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]) and click:
            cost = towers[self.selected_tower].tank_turret.cost
            if player_base.money >= cost:
                self.placing_tower = not self.placing_tower
                if self.placing_tower:
                    self.immune = True
            else:
                self.placing_tower = False
                self.error_timer = 2
                self.error_message = "Insufficient funds"

        if self.error_timer > 0:
            self.error_timer -= 1 / clock.get_fps()
            error_text = medium_font.render(self.error_message, True, (220, 100, 100))
            self.screen.blit(error_text, (buy_container.centerx - error_text.get_width() / 2, 600))


class Base:
    def __init__(self, screen: pygame.Surface, image: pygame.Surface, shadow: pygame.Surface, game: Game,
                 base_cell: Cell, spawn_cell: Cell,
                 team: Team, water_team: Team):
        self.screen = screen
        self.base_image = image
        self.base_shadow = shadow
        self.game = game
        self.base_cell = base_cell
        self.spawn_cell = spawn_cell
        self.team = team
        self.water_team = water_team
        self.tanks: list[Tank] = []
        self.money = 500

        for cell in self.base_cells():
            cell.state = State.BLOCKED
            cell.linked_base = self

        self.spawn_timer = 0
        self.spawn_delay = 120

        self.health = 5000

        self.passive_income_timer = 5

    def add_tower(self, tower: int, index: int) -> bool:
        cell = self.game.map.get_cell(index)
        if cell.linked_tower is not None or cell.state != State.OPEN:
            return False

        cell.state = State.DESTRUCTIBLE

        success = self.game.flood_fill()

        if not success:
            cell.state = State.OPEN
            self.game.flood_fill()
            return False

        tank_data = towers[tower]
        pos = self.game.map.rect_to_pos(self.game.map.index_to_rect(index))
        pos = (pos[0] + self.game.map.size, pos[1] + self.game.map.size)
        tank = Tank(self.screen, self, pos, tank_data)
        tank.linked_cell = cell
        cell.linked_tower = tank
        self.tanks.append(tank)

        return True

    def damage(self, amount: int):
        self.health -= amount
        if self.health <= 0 and state_manager is not None:
            state_manager.game_over(self.other_base().team)

    def bounding_box(self) -> pygame.Rect:
        size = self.game.map.size
        base_cell_pos = self.game.map.index_to_rect(self.base_cell.index)
        corner_cell_pos = (base_cell_pos[0] - 2, base_cell_pos[1] - 1)
        world_pos = self.game.map.rect_to_pos(corner_cell_pos)
        return pygame.Rect(world_pos[0], world_pos[1], size * 5, size * 3)

    def base_cells(self) -> list[Cell]:
        cells: list[Cell] = []
        base_cell_pos = self.game.map.index_to_rect(self.base_cell.index)
        for x in range(-2, 3):
            for y in range(-1, 2):
                cell = self.game.map.get_cell(self.game.map.rect_to_index((base_cell_pos[0] + x, base_cell_pos[1] + y)))
                cells.append(cell)
        return cells

    def spawn(self, upgrades: tuple[int, int]):
        tank_data = TankData(tank_bases[upgrades[0]], tank_turrets[upgrades[1]])
        pos = self.game.map.rect_to_pos(self.game.map.index_to_rect(self.spawn_cell.index))
        pos = (pos[0] + self.game.map.size, pos[1] + self.game.map.size)
        self.tanks.append(Tank(self.screen, self, pos, tank_data))

    def other_base(self):
        other_bases = filter(lambda b: b.team != self.team, self.game.bases)

        for base in other_bases:
            return base

    def flood_fill(self) -> bool:
        success = True
        if not self.game.map.flood_fill(self.spawn_cell.index, self.other_base().base_cell.index, self.team):
            success = False
        if not self.game.map.flood_fill(self.spawn_cell.index, self.other_base().base_cell.index, self.water_team):
            success = False
        return success

    def update(self):
        # if self.spawn_timer <= 0:
        #     self.spawn_timer = self.spawn_delay
        #     self.spawn((self.game.selected_base, self.game.selected_turret))
        # else:
        #     self.spawn_timer -= 1

        if self.passive_income_timer > 0:
            self.passive_income_timer -= 1 / clock.get_fps()
        else:
            self.money += 100
            self.passive_income_timer = 5

        for tank in self.tanks:
            tank.update()
            if tank.health <= 0:
                value = (tank.data.cost + tank.turret.data.cost) * 0.25
                tank.base.other_base().money += round(value)
                cell = tank.closest_cell
                if cell is not None:
                    cell.linked_tanks.remove(tank)
                if tank.linked_cell:
                    tank.linked_cell.state = State.OPEN
                    tank.linked_cell.linked_tower = None
                    self.game.flood_fill()
                self.tanks.remove(tank)

    def draw(self):
        base_cell_pos = self.game.map.index_to_rect(self.base_cell.index)
        base_cell_offset = self.game.map.get_cell(
            self.game.map.rect_to_index((base_cell_pos[0] - 2, base_cell_pos[1] - 1)))

        pos = self.game.map.rect_to_pos(self.game.map.index_to_rect(base_cell_offset.index))
        self.screen.blit(self.base_shadow, (pos[0] - 1, pos[1] + 1))
        self.screen.blit(self.base_image, pos)

        for tank in self.tanks:
            tank.draw()


class Tank:
    def __init__(self, screen: pygame.Surface, base: Base, pos: tuple[int, int],
                 data: TankData, angle: float = 0, size: int = 32):

        self.screen = screen
        self.base = base
        self.image = None if (not data.tank_base.display) or len(data.tank_base.images) == 0 else pygame.image.load(
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
        self.linked_cell: Cell | None = None

        # Targeting
        self.moving = True
        self.target_pos = self.get_center()
        self.target_angle = self.angle
        self.auto = True

    def damage(self, amount: int):
        self.health -= amount

    def bounding_box(self) -> pygame.Rect:
        return pygame.Rect(self.pos[0] - self.size, self.pos[1] - self.size, self.size, self.size)

    def get_angle(self):
        return 90 - self.angle

    def get_center(self):
        return self.pos[0] - self.size / 2, self.pos[1] - self.size / 2

    def shoot(self):
        if self.fire_timer <= 0:
            self.projectiles.append(Projectile(self.screen, self, 10, 2))
            self.fire_timer = self.turret.data.fire_cooldown / 2

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
                        team = self.base.water_team if self.data.hover else self.base.team

                        path = self.base.game.map.traverse(self.closest_cell.index,
                                                           self.base.other_base().base_cell.index,
                                                           team, 1)
                        if len(path) > 1:
                            if path[1].state == State.DESTRUCTIBLE:
                                pos = self.base.game.map.rect_to_pos(self.base.game.map.index_to_rect(path[0].index))
                                self.move_to(
                                    (pos[0] + self.base.game.map.size / 2, pos[1] + self.base.game.map.size / 2))
                            else:
                                pos = self.base.game.map.rect_to_pos(self.base.game.map.index_to_rect(path[1].index))
                                self.move_to((pos[0] + self.base.game.map.size / 2, pos[1] + self.base.game.map.size / 2))


                else:
                    self.move_by(self.data.speed)
            else:
                amount = abs(sin) / sin * self.data.rotation_speed
                self.rotate_by(amount)

        self.turret.update()

        projectiles_to_remove = []
        for projectile in self.projectiles:
            projectile.update()
            if projectile.die:
                projectiles_to_remove.append(projectile)

        for projectile in projectiles_to_remove:
            self.projectiles.remove(projectile)

        if self.fire_timer > 0:
            self.fire_timer -= 1

    def draw(self):
        if self.data.display and self.image is not None:
            center = self.get_center()
            rotated = pygame.transform.rotate(self.image, self.get_angle() + (180 if self.data.name == "Hover" else 0))
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
        enemy_base_cells = self.base.other_base().base_cells()
        closest_cell: Cell | None = None
        closest_cell_dist = math.inf
        for cell in enemy_base_cells:
            cell_pos = self.base.game.map.rect_to_pos(self.base.game.map.index_to_rect(cell.index))
            pos1 = (cell_pos[0] + self.base.game.map.size / 2, cell_pos[1] + self.base.game.map.size / 2)
            pos2 = self.get_center()
            dist = math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2)
            if dist < closest_cell_dist:
                closest_cell_dist = dist
                closest_cell = cell

        other_tanks = self.base.other_base().tanks
        closest_tank: Tank | None = None
        closest_tank_dist = math.inf
        for tank in other_tanks:
            pos1 = tank.get_center()
            pos2 = self.get_center()
            dist = math.pow(pos2[0] - pos1[0], 2) + math.pow(pos2[1] - pos1[1], 2)
            if dist < closest_tank_dist:
                closest_tank_dist = dist
                closest_tank = tank

        target: None | tuple[float, float] = None
        closest_dist = math.inf
        if closest_tank is not None and closest_tank_dist < closest_cell_dist:
            target = closest_tank.get_center()
            closest_dist = closest_tank_dist
        elif closest_cell is not None and closest_cell_dist < closest_tank_dist:
            cell_pos = self.base.game.map.rect_to_pos(self.base.game.map.index_to_rect(closest_cell.index))
            target = (cell_pos[0] + self.base.game.map.size / 2, cell_pos[1] + self.base.game.map.size / 2)
            closest_dist = closest_cell_dist

        if target is not None and closest_dist <= math.pow(self.turret.data.range, 2):
            self.turret.idle = False
            self.turret.aim_at(tuple[int, int](target))
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
        self.angle_offset = random.randrange(360) if self.data.name == "Hedgehog" else angle
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
            self.aim_at(self.tank.base.game.map.rect_to_pos(self.tank.base.game.map.index_to_rect(self.tank.base.other_base().base_cell.index)))

        sin = math.sin(math.radians(self.target_angle - (self.angle_offset - self.tank.get_angle())))
        targeted = round(sin * 10) / 10 == 0
        if not targeted:
            amount = abs(sin) / sin * self.data.rotation_speed
            self.rotate_by(amount)

    def draw(self):
        if self.data.display and self.image is not None:
            center = self.get_center()
            rotated = pygame.transform.rotate(self.image, self.get_angle())
            centered_rect = rotated.get_rect(center=(center[0], center[1]))
            self.screen.blit(rotated, centered_rect)

    def rotate_by(self, amount: float):
        self.angle_offset += amount

    def aim_at(self, target_pos: tuple[int, int]):
        center = self.get_center()
        self.target_angle = math.degrees(math.atan2(target_pos[1] - center[1], target_pos[0] - center[0])) + (
                random.randint(-100, 100) / 1000)


class Fire:
    def __init__(self, screen: pygame.Surface, parent_turret: Turret, image: pygame.Surface, size: int = -1):
        self.screen = screen
        self.turret_or_tower = parent_turret
        self.image = image
        self.size = size

    def draw(self):
        rotated = pygame.transform.rotate(self.image, self.turret_or_tower.get_angle())

        barrel = self.turret_or_tower.get_barrel()
        n = 0
        for offset in self.turret_or_tower.data.barrels:
            tangent_angle = (((-self.turret_or_tower.get_angle()) % 360) + 360) % 360
            tangent_length = math.sqrt(offset[0] ** 2 + offset[1] ** 2)
            barrel_x = barrel[0] + tangent_length * math.cos(math.radians(tangent_angle)) * (-1 if n % 2 == 1 else 1)
            barrel_y = barrel[1] + tangent_length * math.sin(math.radians(tangent_angle)) * (-1 if n % 2 == 1 else 1)

            centered_rect = rotated.get_rect(center=(barrel_x, barrel_y))
            self.screen.blit(rotated, centered_rect)

            n += 1


class Projectile:
    def __init__(self, screen: pygame.Surface, tank: Tank, speed: float, size: int):
        self.screen = screen
        self.tank = tank
        self.pos = tank.get_center() if len(tank.turret.data.barrels) == 0 else tank.turret.get_barrel()
        self.init_pos = self.pos
        self.angle = tank.turret.get_angle()
        self.speed = speed
        self.size = size
        self.die = False
        src = self.tank.turret.data.projectile_image
        self.image = None if src is None else pygame.image.load(src)

    def draw(self):
        if self.image is not None:
            rotated = pygame.transform.rotate(self.image, self.angle)
            center_rect = rotated.get_rect(center=(self.pos[0], self.pos[1]))
            self.screen.blit(rotated, center_rect)
        else:
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
        close_base: Base | None = None

        for cell in total:
            close_tanks.extend(cell.linked_tanks)
            if cell.linked_base is not None:
                close_base = cell.linked_base

        for tank in close_tanks:
            if tank.base.team == self.tank.base.team:
                continue
            bounding_box = tank.bounding_box()
            hit = bounding_box.colliderect((self.pos[0] - 2, self.pos[1] - 2, 4, 4))
            if hit:
                self.die = True
                tank.damage(self.tank.turret.data.damage)
                return

        if close_base is not None and close_base.team != self.tank.base.team:
            bounding_box = close_base.bounding_box()
            hit = bounding_box.colliderect((self.pos[0] - 2, self.pos[1] - 2, 4, 4))
            if hit:
                self.die = True
                close_base.damage(self.tank.turret.data.damage)
                return


class Map:
    """Contains the list of cells in the grid and performs algorithms on them"""

    def __init__(self, screen: pygame.Surface, game: Game, size: int = 32):
        self.screen = screen
        self.game = game
        self.size = size
        self.grid: list[list[Cell]] = []
        self.image = pygame.image.load("../images/Map.png")

        n = self.get_rows()
        for x in range(0, n):
            self.grid.append([])
            for y in range(0, n):
                cell = Cell(self.screen, self.rect_to_index((x, y)))
                cell.state = State(cell_states[x][y])
                self.grid[x].append(cell)

    def print_states(self):
        output = []
        n = self.get_rows()
        for x in range(0, n):
            output.append([])
            for y in range(0, n):
                output[x].append(self.grid[x][y].state.value)
        return output

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
        return self.game.size // self.size

    def draw(self):
        self.screen.blit(self.image, (0, 0))

        s = pygame.Surface((self.game.size, self.game.size))
        s.set_alpha(40)

        n = self.get_rows()
        for x in range(0, n):
            for y in range(0, n):
                rect = (x * self.size, y * self.size, self.size, self.size)
                cell = self.grid[x][y]
                cell.draw(rect, s)

                # text = small_font.render(f"{cell.value[Team.GREEN.value]}", True, (0, 0, 0))
                # text_rect = text.get_rect(center=(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2))
                # self.screen.blit(text, text_rect)

        self.screen.blit(s, (0, 0))

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

    def flood_fill(self, start: int, end: int, team: Team) -> bool:
        reached_start = False
        water = team == Team.RED_WATER or team == Team.GREEN_WATER
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
                    if ((neighbor.state == State.OPEN) or (water and neighbor.state != State.BLOCKED)) and neighbor.value[team] == -1:
                        neighbor.value[team] = cell.value[team] + 1
                        next_cells.append(neighbor)
                        end_cell_blocked = False
                    elif end_cell_blocked:
                        next_cells.append(neighbor)
            if len(next_cells) == 0:
                break
            else:
                if not reached_start:
                    for c in next_cells:
                        if c.index == start:
                            reached_start = True
                cells = next_cells
                next_cells = []
        return reached_start

    def traverse(self, start: int, end: int, team: Team, max_range: int = -1) -> list[Cell]:
        water = team == Team.RED_WATER or team == Team.GREEN_WATER

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
                if ((neighbor.state == State.OPEN) or (water and neighbor.state != State.BLOCKED)) and neighbor.value[
                    team] < cell.value[team]:
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
        self.game: Game = Game(screen)
        self.scene = "title"
        self.winner: str = ""

    def get_event(self, event):
        if self.scene == "title":
            if keys[pygame.K_SPACE]:
                self.scene = "game"
                self.game = Game(self.screen)
            if keys[pygame.K_h]:
                self.scene = "help"
        elif self.scene == "help":
            if keys[pygame.K_b]:
                self.scene = "title"
        elif self.scene == "end":
            if keys[pygame.K_SPACE]:
                self.scene = "title"
        elif self.scene == "game":
            self.game.get_event(event)

    def update(self):
        self.screen.fill((255, 255, 255))
        if self.scene == "title":
            self.title_screen()
        elif self.scene == "help":
            self.help_screen()
        elif self.scene == "end":
            self.end_screen()
        elif self.scene == "game":
            self.game.update()
            self.game.draw()

    def title_screen(self):
        self.screen.fill((59, 76, 99))
        title = pygame.image.load("../images/Title.png")
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 200))
        button_text = font.render("Press 'SPACE' to Start", True, (255, 255, 255))
        self.screen.blit(button_text, (self.screen.get_width() // 2 - button_text.get_width() // 2, 435))
        get_help = font.render("Press 'H' for Help", True, (255, 255, 255))
        self.screen.blit(get_help, (self.screen.get_width() // 2 - get_help.get_width() // 2, 500))

    def help_screen(self):
        self.screen.fill((59, 76, 99))
        title = font.render("Help", True, (255, 201, 14))
        self.screen.blit(title, (575, 25))
        description = pygame.image.load("../images/2023-06-15 (1).png")
        self.screen.blit(description, (20, 5))
        back = font.render("Press 'B' to Go Back", True, (255, 255, 255))
        self.screen.blit(back, (525, 575))

    def end_screen(self):
        if self.winner == "RED":
            color = (237, 28, 36)
        else:
            color = (28, 237, 36)

        self.screen.fill((59, 76, 99))
        title = pygame.image.load("../images/Game_Over.png")
        win_text = font.render(f"{self.winner} Team Won!", True, color)
        self.screen.blit(title, (self.screen.get_width() // 2 - title.get_width() // 2, 200))
        self.screen.blit(win_text, (self.screen.get_width() // 2 - win_text.get_width() // 2, 200 + title.get_height() * 1.5))
        button_text = font.render("Press 'SPACE' to Return to Title Screen", True, (255, 255, 255))
        self.screen.blit(button_text, (self.screen.get_width() // 2 - button_text.get_width() // 2, 435))

    def game_over(self, winner: Team):
        self.scene = "end"
        self.winner = winner.name


state_manager: StateManager | None = None


def main():
    # Global variables that will be set here
    global state_manager
    global click
    global keys

    # Start pygame
    pygame.init()

    # Setup window, screen
    pygame.display.set_caption("Tank Tower Defense")
    screen = pygame.display.set_mode((640 + 190, 640))

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
