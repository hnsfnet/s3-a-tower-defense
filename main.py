import pygame
import sys
from config import *
from game_map import GameMap
from tower import Tower, Projectile, Explosion, LightningEffect
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
        self.paused = False
        self.speed_multiplier = 1

        self._init_game()

    def _init_game(self):
        self.game_map = GameMap()
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.explosions = []
        self.effects = []
        self.wave_manager = WaveManager(self.game_map.path_points)

        self.gold = INITIAL_GOLD
        self.lives = INITIAL_LIVES

        self.selected_tile = None
        self.show_tower_menu = False
        self.show_upgrade_menu = False
        self.menu_position = (0, 0)
        self.hovered_tower_type = None
        self.hovered_upgrade_btn = False
        self.selected_tower = None

    def run(self):
        running = True
        while running:
            raw_dt = self.clock.tick(FPS) / 1000.0
            dt = raw_dt * self.speed_multiplier if not self.paused else 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == 'menu':
                    self._handle_menu_event(event)
                elif self.state == 'playing':
                    self._handle_game_event(event)
                elif self.state in ('won', 'lost'):
                    self._handle_end_event(event)

            if self.state == 'playing' and not self.paused:
                self._update(dt)

            self._draw()
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
                if not self.wave_manager.wave_active and not self.wave_manager.is_game_won():
                    self.wave_manager.start_wave()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos

            if mouse_y < TOP_UI_HEIGHT:
                self.show_tower_menu = False
                self.show_upgrade_menu = False
                self.selected_tile = None
                self.selected_tower = None
                return

            grid_x = mouse_x // TILE_SIZE
            grid_y = (mouse_y - TOP_UI_HEIGHT) // TILE_SIZE

            if self.show_upgrade_menu and self.selected_tower:
                if self._is_upgrade_button_clicked(mouse_x, mouse_y):
                    self._try_upgrade_tower()
                    return
                self.show_upgrade_menu = False
                self.selected_tower = None

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

        elif event.type == pygame.MOUSEMOTION:
            if self.show_tower_menu:
                self.hovered_tower_type = self._get_menu_clicked_tower(event.pos[0], event.pos[1])
            elif self.show_upgrade_menu:
                self.hovered_upgrade_btn = self._is_upgrade_button_clicked(event.pos[0], event.pos[1])

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

        menu_x, menu_y = self._get_place_menu_position()
        tower_types = list(TOWER_TYPES.keys())

        for i, tower_type in enumerate(tower_types):
            btn_y = menu_y + 10 + i * 55
            btn_rect = pygame.Rect(menu_x + 10, btn_y, 180, 45)
            if btn_rect.collidepoint(mouse_x, mouse_y):
                return tower_type

        return None

    def _get_place_menu_position(self):
        menu_width = 200
        menu_height = 10 + len(TOWER_TYPES) * 55 + 10

        menu_x = self.menu_position[0]
        menu_y = self.menu_position[1]

        if menu_x + menu_width > SCREEN_WIDTH:
            menu_x = SCREEN_WIDTH - menu_width
        if menu_y + menu_height > SCREEN_HEIGHT:
            menu_y = SCREEN_HEIGHT - menu_height

        return (menu_x, menu_y)

    def _get_upgrade_menu_position(self):
        menu_width = 200
        menu_height = 110

        menu_x = self.menu_position[0]
        menu_y = self.menu_position[1]

        if menu_x + menu_width > SCREEN_WIDTH:
            menu_x = SCREEN_WIDTH - menu_width
        if menu_y + menu_height > SCREEN_HEIGHT:
            menu_y = SCREEN_HEIGHT - menu_height

        return (menu_x, menu_y)

    def _is_upgrade_button_clicked(self, mouse_x, mouse_y):
        if not self.show_upgrade_menu or not self.selected_tower:
            return False

        menu_x, menu_y = self._get_upgrade_menu_position()
        btn_rect = pygame.Rect(menu_x + 10, menu_y + 60, 180, 40)
        return btn_rect.collidepoint(mouse_x, mouse_y)

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

    def _try_upgrade_tower(self):
        if not self.selected_tower:
            return

        if not self.selected_tower.can_upgrade():
            return

        cost = self.selected_tower.get_upgrade_cost()
        if self.gold < cost:
            return

        self.gold -= cost
        self.selected_tower.upgrade()

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
            rewards = tower.update(dt, self.enemies, self.projectiles, self.effects)
            for reward in rewards:
                self.gold += reward

        for proj in self.projectiles:
            rewards = proj.update(dt, self.enemies)
            for reward in rewards:
                self.gold += reward

        self.projectiles = [p for p in self.projectiles if p.active]

        for explosion in self.explosions:
            explosion.update(dt)
        self.explosions = [e for e in self.explosions if e.active]

        for effect in self.effects:
            effect.update(dt)
        self.effects = [e for e in self.effects if e.active]

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
        info2 = self.font_small.render('Press ENTER to start next wave', True, COLORS['text'])
        info3 = self.font_small.render('Press SPACE to pause | Press F for 2x speed', True, COLORS['text'])

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        info1_rect = info1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        info2_rect = info2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        info3_rect = info3.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(info1, info1_rect)
        self.screen.blit(info2, info2_rect)
        self.screen.blit(info3, info3_rect)

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

        for effect in self.effects:
            effect.draw(self.screen)

        if self.show_tower_menu and self.selected_tile:
            self._draw_tower_place_menu()

        if self.show_upgrade_menu and self.selected_tower:
            self._draw_tower_upgrade_menu()

        if self.paused:
            self._draw_pause_overlay()

    def _draw_ui(self):
        pygame.draw.rect(self.screen, COLORS['ui_bg'], (0, 0, SCREEN_WIDTH, TOP_UI_HEIGHT))

        wave_text = self.font_medium.render(
            f'Wave: {self.wave_manager.current_wave}/{self.wave_manager.total_waves}', True, COLORS['text'])
        self.screen.blit(wave_text, (20, 5))

        remaining = self.wave_manager.get_remaining_enemies(self.enemies)
        enemy_text = self.font_medium.render(f'Enemies: {remaining}', True, COLORS['text'])
        self.screen.blit(enemy_text, (20, 40))

        gold_text = self.font_medium.render(f'Gold: {self.gold}', True, (255, 215, 0))
        gold_rect = gold_text.get_rect()
        gold_rect.right = SCREEN_WIDTH - 20
        gold_rect.top = 5
        self.screen.blit(gold_text, gold_rect)

        lives_text = self.font_medium.render(f'Lives: {self.lives}', True, (255, 100, 100))
        lives_rect = lives_text.get_rect()
        lives_rect.right = SCREEN_WIDTH - 20
        lives_rect.top = 40
        self.screen.blit(lives_text, lives_rect)

        speed_text = self.font_small.render(f'Speed: {self.speed_multiplier}x', True, (150, 200, 255))
        speed_rect = speed_text.get_rect()
        speed_rect.centerx = SCREEN_WIDTH // 2 - 50
        speed_rect.top = 8
        self.screen.blit(speed_text, speed_rect)

        if self.paused:
            pause_text = self.font_small.render('PAUSED', True, (255, 100, 100))
        else:
            pause_text = self.font_small.render('Running', True, (100, 255, 100))
        pause_rect = pause_text.get_rect()
        pause_rect.centerx = SCREEN_WIDTH // 2 + 50
        pause_rect.top = 8
        self.screen.blit(pause_text, pause_rect)

        if not self.wave_manager.wave_active and not self.wave_manager.is_game_won():
            hint = self.font_small.render('Press ENTER to start wave | SPACE: Pause | F: 2x Speed', True, (200, 200, 100))
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, TOP_UI_HEIGHT - 15))
            self.screen.blit(hint, hint_rect)

    def _draw_tower_place_menu(self):
        menu_x, menu_y = self._get_place_menu_position()
        tower_types = list(TOWER_TYPES.keys())
        menu_width = 200
        menu_height = 10 + len(tower_types) * 55 + 10

        pygame.draw.rect(self.screen, COLORS['menu_bg'],
                        (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, COLORS['menu_border'],
                        (menu_x, menu_y, menu_width, menu_height), 2)

        for i, tower_type in enumerate(tower_types):
            stats = TOWER_TYPES[tower_type]
            level1 = stats['levels'][0]
            btn_y = menu_y + 10 + i * 55
            btn_rect = pygame.Rect(menu_x + 10, btn_y, 180, 45)

            is_hovered = (self.hovered_tower_type == tower_type)
            if is_hovered:
                pygame.draw.rect(self.screen, COLORS['button_hover'], btn_rect)

            pygame.draw.rect(self.screen, stats['base_color'],
                           (btn_rect.x + 5, btn_rect.y + 12, 22, 22))

            name_text = self.font_small.render(stats['name'], True, COLORS['text'])
            self.screen.blit(name_text, (btn_rect.x + 35, btn_rect.y + 3))

            stat_text = self.font_small.render(
                f'DMG:{level1["damage"]} RNG:{level1["range"]}', True, (200, 200, 200))
            self.screen.blit(stat_text, (btn_rect.x + 35, btn_rect.y + 18))

            cost_color = (255, 215, 0) if self.gold >= stats['cost'] else (200, 50, 50)
            cost_text = self.font_small.render(f'${stats["cost"]}', True, cost_color)
            self.screen.blit(cost_text, (btn_rect.x + 130, btn_rect.y + 3))

    def _draw_tower_upgrade_menu(self):
        menu_x, menu_y = self._get_upgrade_menu_position()
        menu_width = 200
        menu_height = 110
        tower = self.selected_tower

        pygame.draw.rect(self.screen, COLORS['menu_bg'],
                        (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, COLORS['menu_border'],
                        (menu_x, menu_y, menu_width, menu_height), 2)

        title_text = self.font_small.render(f'{tower.name} Lv.{tower.level}', True, COLORS['text'])
        self.screen.blit(title_text, (menu_x + 10, menu_y + 8))

        stats_text = self.font_small.render(
            f'DMG:{tower.damage} RNG:{tower.range} SPD:{1/tower.fire_rate:.1f}/s',
            True, (200, 200, 200))
        self.screen.blit(stats_text, (menu_x + 10, menu_y + 28))

        btn_rect = pygame.Rect(menu_x + 10, menu_y + 60, 180, 40)

        if tower.can_upgrade():
            upgrade_cost = tower.get_upgrade_cost()
            can_afford = self.gold >= upgrade_cost

            if self.hovered_upgrade_btn and can_afford:
                pygame.draw.rect(self.screen, COLORS['button_hover'], btn_rect)
            elif not can_afford:
                pygame.draw.rect(self.screen, COLORS['upgrade_disabled'], btn_rect)
            else:
                pygame.draw.rect(self.screen, COLORS['upgrade_button'], btn_rect)

            btn_color = (255, 255, 255) if can_afford else (150, 150, 150)
            upgrade_text = self.font_medium.render(f'Upgrade ${upgrade_cost}', True, btn_color)
        else:
            pygame.draw.rect(self.screen, COLORS['upgrade_disabled'], btn_rect)
            upgrade_text = self.font_medium.render('Max Level', True, (200, 200, 200))

        text_rect = upgrade_text.get_rect(center=btn_rect.center)
        self.screen.blit(upgrade_text, text_rect)

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOP_UI_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, TOP_UI_HEIGHT))

        pause_text = self.font_large.render('PAUSED', True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)

        hint_text = self.font_small.render('Press SPACE to resume', True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        self.screen.blit(hint_text, hint_rect)

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
