import pygame
import sys
from config import *
from game_map import GameMap
from tower import Tower, Projectile, Explosion
from wave_manager import WaveManager


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tower Defense')
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 48)

        self.state = 'menu'

        self._init_game()

    def _init_game(self):
        self.game_map = GameMap()
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.explosions = []
        self.wave_manager = WaveManager(self.game_map.path_points)

        self.gold = INITIAL_GOLD
        self.lives = INITIAL_LIVES

        self.selected_tile = None
        self.show_tower_menu = False
        self.menu_position = (0, 0)
        self.hovered_tower_type = None
        self.selected_tower = None

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == 'menu':
                    self._handle_menu_event(event)
                elif self.state == 'playing':
                    self._handle_game_event(event)
                elif self.state in ('won', 'lost'):
                    self._handle_end_event(event)

            if self.state == 'playing':
                self._update(dt)

            self._draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.state = 'playing'

    def _handle_game_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            if mouse_y < TOP_UI_HEIGHT:
                self.show_tower_menu = False
                self.selected_tile = None
                self.selected_tower = None
                return

            grid_x = mouse_x // TILE_SIZE
            grid_y = (mouse_y - TOP_UI_HEIGHT) // TILE_SIZE

            if self.show_tower_menu:
                tower_type = self._get_menu_clicked_tower(mouse_x, mouse_y)
                if tower_type:
                    self._place_tower(tower_type)
                self.show_tower_menu = False
                self.selected_tile = None
                return

            existing_tower = self._get_tower_at(grid_x, grid_y)
            if existing_tower:
                self.selected_tower = existing_tower
                self.show_tower_menu = False
                return

            if self.game_map.is_placeable(grid_x, grid_y):
                self.selected_tile = (grid_x, grid_y)
                self.show_tower_menu = True
                self.menu_position = (mouse_x, mouse_y)
                self.selected_tower = None
            else:
                self.show_tower_menu = False
                self.selected_tile = None
                self.selected_tower = None

        elif event.type == pygame.MOUSEMOTION:
            if self.show_tower_menu:
                self.hovered_tower_type = self._get_menu_clicked_tower(event.pos[0], event.pos[1])

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not self.wave_manager.wave_active and not self.wave_manager.is_game_won():
                    self.wave_manager.start_wave()

    def _handle_end_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._init_game()
            self.state = 'menu'

    def _get_tower_at(self, grid_col, grid_row):
        for tower in self.towers:
            if tower.grid_col == grid_col and tower.grid_row == grid_row:
                return tower
        return None

    def _get_menu_clicked_tower(self, mouse_x, mouse_y):
        if not self.show_tower_menu:
            return None

        menu_x, menu_y = self._get_menu_position()
        tower_types = list(TOWER_TYPES.keys())

        for i, tower_type in enumerate(tower_types):
            btn_y = menu_y + 10 + i * 50
            btn_rect = pygame.Rect(menu_x + 10, btn_y, 160, 40)
            if btn_rect.collidepoint(mouse_x, mouse_y):
                return tower_type

        return None

    def _get_menu_position(self):
        menu_width = 180
        menu_height = 10 + len(TOWER_TYPES) * 50 + 10

        menu_x = self.menu_position[0]
        menu_y = self.menu_position[1]

        if menu_x + menu_width > SCREEN_WIDTH:
            menu_x = SCREEN_WIDTH - menu_width
        if menu_y + menu_height > SCREEN_HEIGHT:
            menu_y = SCREEN_HEIGHT - menu_height

        return (menu_x, menu_y)

    def _place_tower(self, tower_type):
        if not self.selected_tile:
            return

        cost = TOWER_TYPES[tower_type]['cost']
        if self.gold < cost:
            return

        grid_col, grid_row = self.selected_tile
        if self._get_tower_at(grid_col, grid_row):
            return

        tower = Tower(grid_col, grid_row, tower_type)
        self.towers.append(tower)
        self.gold -= cost

    def _update(self, dt):
        self.wave_manager.update(dt, self.enemies)

        for enemy in self.enemies:
            enemy.update(dt)
            if enemy.reached_end and enemy.alive:
                enemy.alive = False
                self.lives -= 1
                if self.lives <= 0:
                    self.lives = 0
                    self.state = 'lost'

        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles, self.explosions)

        for proj in self.projectiles:
            rewards = proj.update(dt, self.enemies)
            for reward in rewards:
                self.gold += reward

        self.projectiles = [p for p in self.projectiles if p.active]

        for explosion in self.explosions:
            explosion.update(dt)
        self.explosions = [e for e in self.explosions if e.active]

        self.enemies = [e for e in self.enemies if e.alive or (not e.alive and not e.reached_end)]

        if self.wave_manager.is_wave_complete(self.enemies):
            self.wave_manager.end_wave()
            if self.wave_manager.is_game_won():
                self.state = 'won'

        self.enemies = [e for e in self.enemies if e.alive]

    def _draw(self):
        self.screen.fill(COLORS['background'])

        if self.state == 'menu':
            self._draw_menu()
        elif self.state == 'playing':
            self._draw_game()
        elif self.state == 'won':
            self._draw_game()
            self._draw_end_screen('Victory!', (0, 200, 0))
        elif self.state == 'lost':
            self._draw_game()
            self._draw_end_screen('Defeat!', (200, 0, 0))

    def _draw_menu(self):
        title = self.font_large.render('Tower Defense', True, COLORS['text'])
        subtitle = self.font_medium.render('Click to Start', True, COLORS['text'])
        info1 = self.font_small.render('Click empty land to place towers', True, COLORS['text'])
        info2 = self.font_small.render('Press SPACE to start next wave', True, COLORS['text'])

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        info1_rect = info1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        info2_rect = info2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(info1, info1_rect)
        self.screen.blit(info2, info2_rect)

    def _draw_game(self):
        self._draw_ui()
        self.game_map.draw(self.screen)

        for tower in self.towers:
            tower.draw(self.screen)

        if self.selected_tower:
            self.selected_tower.draw_range(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for proj in self.projectiles:
            proj.draw(self.screen)

        for explosion in self.explosions:
            explosion.draw(self.screen)

        if self.show_tower_menu and self.selected_tile:
            self._draw_tower_menu()

    def _draw_ui(self):
        pygame.draw.rect(self.screen, COLORS['ui_bg'], (0, 0, SCREEN_WIDTH, TOP_UI_HEIGHT))

        wave_text = self.font_medium.render(f'Wave: {self.wave_manager.current_wave}/{self.wave_manager.total_waves}', True, COLORS['text'])
        self.screen.blit(wave_text, (20, 10))

        remaining = self.wave_manager.get_remaining_enemies(self.enemies)
        enemy_text = self.font_medium.render(f'Enemies: {remaining}', True, COLORS['text'])
        self.screen.blit(enemy_text, (20, 45))

        gold_text = self.font_medium.render(f'Gold: {self.gold}', True, (255, 215, 0))
        gold_rect = gold_text.get_rect()
        gold_rect.right = SCREEN_WIDTH - 20
        gold_rect.top = 10
        self.screen.blit(gold_text, gold_rect)

        lives_text = self.font_medium.render(f'Lives: {self.lives}', True, (255, 100, 100))
        lives_rect = lives_text.get_rect()
        lives_rect.right = SCREEN_WIDTH - 20
        lives_rect.top = 45
        self.screen.blit(lives_text, lives_rect)

        if not self.wave_manager.wave_active and not self.wave_manager.is_game_won():
            hint = self.font_small.render('Press SPACE to start wave', True, (200, 200, 100))
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, TOP_UI_HEIGHT - 15))
            self.screen.blit(hint, hint_rect)

    def _draw_tower_menu(self):
        menu_x, menu_y = self._get_menu_position()
        tower_types = list(TOWER_TYPES.keys())
        menu_width = 180
        menu_height = 10 + len(tower_types) * 50 + 10

        pygame.draw.rect(self.screen, COLORS['menu_bg'],
                        (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, COLORS['menu_border'],
                        (menu_x, menu_y, menu_width, menu_height), 2)

        for i, tower_type in enumerate(tower_types):
            stats = TOWER_TYPES[tower_type]
            btn_y = menu_y + 10 + i * 50
            btn_rect = pygame.Rect(menu_x + 10, btn_y, 160, 40)

            is_hovered = (self.hovered_tower_type == tower_type)
            if is_hovered:
                pygame.draw.rect(self.screen, COLORS['button_hover'], btn_rect)

            pygame.draw.rect(self.screen, stats['color'],
                           (btn_rect.x + 5, btn_rect.y + 10, 20, 20))

            name_text = self.font_small.render(stats['name'], True, COLORS['text'])
            self.screen.blit(name_text, (btn_rect.x + 35, btn_rect.y + 5))

            cost_color = (255, 215, 0) if self.gold >= stats['cost'] else (200, 50, 50)
            cost_text = self.font_small.render(f'${stats["cost"]}', True, cost_color)
            self.screen.blit(cost_text, (btn_rect.x + 35, btn_rect.y + 22))

    def _draw_end_screen(self, message, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render(message, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(text, text_rect)

        restart_text = self.font_medium.render('Click to restart', True, COLORS['text'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)


if __name__ == '__main__':
    game = Game()
    game.run()
