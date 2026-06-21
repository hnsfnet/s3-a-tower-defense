import pygame
import sys

from config import *
from game_map import GameMap
from ui_renderer import UIRenderer
from systems import (
    CombatSystem,
    RenderSystem,
    WaveSystem,
    EconomySystem,
)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tower Defense')
        self.clock = pygame.time.Clock()

        self.ui_renderer = UIRenderer()
        self.combat = CombatSystem()
        self.economy = EconomySystem()
        self.render_system = RenderSystem(self.ui_renderer)

        self.state = 'menu'
        self.paused = False
        self.speed_multiplier = 1

        self._init_game()

    def _init_game(self):
        self.game_map = GameMap()
        self.wave_system = WaveSystem(self.game_map.path_points)
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.effects = []
        self.economy.reset()

        self.selected_tile = None
        self.show_tower_menu = False
        self.show_upgrade_menu = False
        self.menu_position = (0, 0)
        self.hovered_tower_type = None
        self.hovered_upgrade_btn = False
        self.selected_tower = None

    def _get_game_data(self):
        return {
            'game_map': self.game_map,
            'towers': self.towers,
            'enemies': self.enemies,
            'projectiles': self.projectiles,
            'effects': self.effects,
            'economy': self.economy,
            'wave_system': self.wave_system,
            'speed_multiplier': self.speed_multiplier,
            'selected_tower': self.selected_tower,
            'show_tower_menu': self.show_tower_menu,
            'show_upgrade_menu': self.show_upgrade_menu,
            'menu_position': self.menu_position,
            'hovered_tower_type': self.hovered_tower_type,
            'hovered_upgrade_btn': self.hovered_upgrade_btn,
        }

    def run(self):
        running = True
        while running:
            raw_dt = self.clock.tick(FPS) / 1000.0
            dt = raw_dt * self.speed_multiplier if not self.paused else 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif self.state == 'menu':
                    self._handle_menu_event(event)
                elif self.state == 'playing':
                    self._handle_game_event(event)
                elif self.state in ('won', 'lost'):
                    self._handle_end_event(event)

            if self.state == 'playing' and not self.paused:
                self._update(dt)

            self.render_system.draw_full_game(
                self.screen, self._get_game_data(), self.state, self.paused)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.state = 'playing'

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
                self.show_tower_menu = False
                self.show_upgrade_menu = False
                self.selected_tile = None
                return
            elif event.key == pygame.K_f:
                self.speed_multiplier = 2 if self.speed_multiplier == 1 else 1
                return
            elif event.key == pygame.K_RETURN:
                if self.wave_system.can_start_next_wave():
                    self.wave_system.start_wave()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            self._handle_click(mouse_x, mouse_y)

        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_move(event.pos[0], event.pos[1])

    def _handle_end_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._init_game()
            self.state = 'menu'

    def _get_tower_at(self, grid_col, grid_row):
        for tower in self.towers:
            if tower.grid_col == grid_col and tower.grid_row == grid_row:
                return tower
        return None

    def _handle_click(self, mouse_x, mouse_y):
        if mouse_y < TOP_UI_HEIGHT:
            self.show_tower_menu = False
            self.show_upgrade_menu = False
            self.selected_tile = None
            self.selected_tower = None
            return

        grid_x = mouse_x // TILE_SIZE
        grid_y = (mouse_y - TOP_UI_HEIGHT) // TILE_SIZE

        if self.show_upgrade_menu and self.selected_tower:
            mx, my = self.ui_renderer.get_upgrade_menu_position(
                self.menu_position[0], self.menu_position[1])
            if self.ui_renderer.is_upgrade_button_clicked(mouse_x, mouse_y, mx, my):
                self.economy.upgrade_tower(self.selected_tower)
                return
            self.show_upgrade_menu = False
            self.selected_tower = None

        if self.show_tower_menu:
            mx, my = self.ui_renderer.get_place_menu_position(
                self.menu_position[0], self.menu_position[1])
            tower_type = self.ui_renderer.is_place_menu_button_clicked(mouse_x, mouse_y, mx, my)
            if tower_type:
                can_place, _ = self.economy.can_place_tower(
                    tower_type, self.game_map,
                    self.selected_tile[0], self.selected_tile[1],
                    self.towers)
                if can_place:
                    tower = self.economy.place_tower(tower_type,
                                                       self.selected_tile[0],
                                                       self.selected_tile[1])
                    if tower:
                        self.towers.append(tower)
            self.show_tower_menu = False
            self.selected_tile = None
            return

        existing_tower = self._get_tower_at(grid_x, grid_y)
        if existing_tower:
            self.selected_tower = existing_tower
            self.show_upgrade_menu = True
            self.show_tower_menu = False
            self.menu_position = (mouse_x, mouse_y)
            return

        if self.game_map.is_placeable(grid_x, grid_y):
            self.selected_tile = (grid_x, grid_y)
            self.show_tower_menu = True
            self.show_upgrade_menu = False
            self.menu_position = (mouse_x, mouse_y)
            self.selected_tower = None
        else:
            self.show_tower_menu = False
            self.show_upgrade_menu = False
            self.selected_tile = None
            self.selected_tower = None

    def _handle_mouse_move(self, mouse_x, mouse_y):
        if self.show_tower_menu:
            mx, my = self.ui_renderer.get_place_menu_position(
                self.menu_position[0], self.menu_position[1])
            self.hovered_tower_type = self.ui_renderer.is_place_menu_button_clicked(
                mouse_x, mouse_y, mx, my)
        elif self.show_upgrade_menu and self.selected_tower:
            mx, my = self.ui_renderer.get_upgrade_menu_position(
                self.menu_position[0], self.menu_position[1])
            self.hovered_upgrade_btn = self.ui_renderer.is_upgrade_button_clicked(
                mouse_x, mouse_y, mx, my)

    def _update(self, dt):
        self.wave_system.update(dt, self.enemies)

        self.combat.update_enemies(dt, self.enemies)
        for enemy in self.enemies:
            if enemy.reached_end and enemy.alive:
                enemy.alive = False
                self.economy.deduct_life()
                if self.economy.is_game_over():
                    self.state = 'lost'

        rewards = self.combat.update(dt, self.towers, self.enemies,
                                     self.projectiles, self.effects)
        for reward in rewards:
            self.economy.add_gold(reward)

        self.projectiles, self.effects = self.combat.cleanup(
            self.projectiles, self.effects)
        self.enemies = self.combat.cleanup_dead_enemies(self.enemies)

        if self.wave_system.check_and_end_wave(self.enemies):
            if self.wave_system.is_game_won():
                self.state = 'won'


if __name__ == '__main__':
    game = Game()
    game.run()
