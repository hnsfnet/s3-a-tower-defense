import pygame
from config import *
from tower import Explosion, LightningEffect, Projectile


class RenderSystem:
    def __init__(self, ui_renderer):
        self.ui = ui_renderer

    def draw_background(self, surface):
        surface.fill(COLORS['background'])

    def draw_map(self, surface, game_map):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                tile_type = game_map.grid[row][col]
                x = col * TILE_SIZE
                y = row * TILE_SIZE + TOP_UI_HEIGHT

                if tile_type == EMPTY:
                    color = COLORS['empty']
                elif tile_type == PATH:
                    color = COLORS['path']
                elif tile_type == START:
                    color = COLORS['start']
                elif tile_type == END:
                    color = COLORS['end']
                else:
                    color = COLORS['empty']

                pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(surface, COLORS['grid_line'], (x, y, TILE_SIZE, TILE_SIZE), 1)

    def draw_towers(self, surface, towers, selected_tower):
        for tower in towers:
            tower.draw(surface)
        if selected_tower:
            selected_tower.draw_range(surface)

    def draw_enemies(self, surface, enemies):
        for enemy in enemies:
            if not enemy.alive:
                continue
            if enemy.slow_timer > 0:
                pygame.draw.circle(surface, COLORS['enemy_slow'],
                                 (int(enemy.x), int(enemy.y)), enemy.size + 3, 2)
            pygame.draw.circle(surface, enemy.color, (int(enemy.x), int(enemy.y)), enemy.size)
            hp_ratio = enemy.hp / enemy.max_hp
            self.ui.draw_enemy_hp_bar(surface, enemy.x, enemy.y, enemy.size, hp_ratio)
            if enemy.enemy_type == 'boss':
                pygame.draw.circle(surface, (255, 255, 255),
                                 (int(enemy.x), int(enemy.y)), enemy.size - 4, 2)

    def draw_projectiles(self, surface, projectiles):
        for proj in projectiles:
            proj.draw(surface)

    def draw_effects(self, surface, effects):
        for effect in effects:
            effect.draw(surface)

    def draw_full_game(self, surface, game_data, state, paused):
        game_map = game_data['game_map']
        towers = game_data['towers']
        enemies = game_data['enemies']
        projectiles = game_data['projectiles']
        effects = game_data['effects']
        economy = game_data['economy']
        wave_system = game_data['wave_system']
        speed_multiplier = game_data.get('speed_multiplier', 1)
        selected_tower = game_data.get('selected_tower', None)
        show_tower_menu = game_data.get('show_tower_menu', False)
        show_upgrade_menu = game_data.get('show_upgrade_menu', False)
        menu_position = game_data.get('menu_position', (0, 0))
        hovered_tower_type = game_data.get('hovered_tower_type', None)
        hovered_upgrade_btn = game_data.get('hovered_upgrade_btn', False)

        self.draw_background(surface)

        if state == 'menu':
            self.ui.draw_menu(surface)
            return

        self.ui.draw_top_ui(surface, economy, wave_system, paused, speed_multiplier)
        self.draw_map(surface, game_map)
        self.draw_towers(surface, towers, selected_tower)
        self.draw_enemies(surface, enemies)
        self.draw_projectiles(surface, projectiles)
        self.draw_effects(surface, effects)

        if show_tower_menu:
            mx, my = self.ui.get_place_menu_position(menu_position[0], menu_position[1])
            self.ui.draw_tower_place_menu(surface, mx, my, hovered_tower_type, economy)

        if show_upgrade_menu and selected_tower:
            mx, my = self.ui.get_upgrade_menu_position(menu_position[0], menu_position[1])
            self.ui.draw_tower_upgrade_menu(surface, mx, my, selected_tower, economy, hovered_upgrade_btn)

        if paused and state == 'playing':
            self.ui.draw_pause_overlay(surface)

        if state == 'won':
            self.ui.draw_end_screen(surface, 'Victory!', (0, 200, 0))
        elif state == 'lost':
            self.ui.draw_end_screen(surface, 'Defeat!', (200, 0, 0))
