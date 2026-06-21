import pygame
from config import *


class UIRenderer:
    def __init__(self):
        self.font_small = pygame.font.Font(None, 20)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 48)

    def draw_menu(self, surface):
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

        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)
        surface.blit(info1, info1_rect)
        surface.blit(info2, info2_rect)
        surface.blit(info3, info3_rect)

    def draw_top_ui(self, surface, economy, wave_system, paused, speed_multiplier):
        pygame.draw.rect(surface, COLORS['ui_bg'], (0, 0, SCREEN_WIDTH, TOP_UI_HEIGHT))

        wave_text = self.font_medium.render(
            f'Wave: {wave_system.current_wave}/{wave_system.total_waves}', True, COLORS['text'])
        surface.blit(wave_text, (20, 5))

        remaining = wave_system.get_remaining_enemies([])
        enemy_text = self.font_medium.render(f'Enemies: {remaining}', True, COLORS['text'])
        surface.blit(enemy_text, (20, 40))

        gold_text = self.font_medium.render(f'Gold: {economy.gold}', True, (255, 215, 0))
        gold_rect = gold_text.get_rect()
        gold_rect.right = SCREEN_WIDTH - 20
        gold_rect.top = 5
        surface.blit(gold_text, gold_rect)

        lives_text = self.font_medium.render(f'Lives: {economy.lives}', True, (255, 100, 100))
        lives_rect = lives_text.get_rect()
        lives_rect.right = SCREEN_WIDTH - 20
        lives_rect.top = 40
        surface.blit(lives_text, lives_rect)

        speed_text = self.font_small.render(f'Speed: {speed_multiplier}x', True, (150, 200, 255))
        speed_rect = speed_text.get_rect()
        speed_rect.centerx = SCREEN_WIDTH // 2 - 50
        speed_rect.top = 8
        surface.blit(speed_text, speed_rect)

        if paused:
            pause_text = self.font_small.render('PAUSED', True, (255, 100, 100))
        else:
            pause_text = self.font_small.render('Running', True, (100, 255, 100))
        pause_rect = pause_text.get_rect()
        pause_rect.centerx = SCREEN_WIDTH // 2 + 50
        pause_rect.top = 8
        surface.blit(pause_text, pause_rect)

        if wave_system.in_cooldown:
            cooldown = wave_system.get_cooldown_remaining()
            hint = self.font_small.render(
                f'Next wave in {cooldown:.1f}s...', True, (200, 200, 100))
        elif not wave_system.wave_active and not wave_system.is_game_won():
            hint = self.font_small.render(
                'Press ENTER to start wave | SPACE: Pause | F: 2x Speed', True, (200, 200, 100))
        else:
            hint = self.font_small.render(
                'SPACE: Pause | F: 2x Speed', True, (200, 200, 100))
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, TOP_UI_HEIGHT - 15))
        surface.blit(hint, hint_rect)

    def draw_enemy_hp_bar(self, surface, x, y, size, hp_ratio):
        bar_width = int(size * 2.2)
        bar_height = 4
        bar_x = x - bar_width / 2
        bar_y = y - size - 8
        pygame.draw.rect(surface, COLORS['enemy_hp_bar_bg'], (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, COLORS['enemy_hp_bar'], (bar_x, bar_y, bar_width * hp_ratio, bar_height))

    def draw_tower_place_menu(self, surface, menu_x, menu_y, hovered_type, economy):
        tower_types = list(TOWER_TYPES.keys())
        menu_width = 200
        menu_height = 10 + len(tower_types) * 55 + 10

        pygame.draw.rect(surface, COLORS['menu_bg'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, COLORS['menu_border'], (menu_x, menu_y, menu_width, menu_height), 2)

        for i, tower_type in enumerate(tower_types):
            stats = TOWER_TYPES[tower_type]
            level1 = stats['levels'][0]
            btn_y = menu_y + 10 + i * 55
            btn_rect = pygame.Rect(menu_x + 10, btn_y, 180, 45)

            is_hovered = (hovered_type == tower_type)
            if is_hovered:
                pygame.draw.rect(surface, COLORS['button_hover'], btn_rect)

            pygame.draw.rect(surface, stats['base_color'], (btn_rect.x + 5, btn_rect.y + 12, 22, 22))

            name_text = self.font_small.render(stats['name'], True, COLORS['text'])
            surface.blit(name_text, (btn_rect.x + 35, btn_rect.y + 3))

            stat_text = self.font_small.render(
                f'DMG:{level1["damage"]} RNG:{level1["range"]}', True, (200, 200, 200))
            surface.blit(stat_text, (btn_rect.x + 35, btn_rect.y + 18))

            cost_color = (255, 215, 0) if economy.can_afford(stats['cost']) else (200, 50, 50)
            cost_text = self.font_small.render(f'${stats["cost"]}', True, cost_color)
            surface.blit(cost_text, (btn_rect.x + 130, btn_rect.y + 3))

    def draw_tower_upgrade_menu(self, surface, menu_x, menu_y, tower, economy, hovered_btn):
        menu_width = 200
        menu_height = 110

        pygame.draw.rect(surface, COLORS['menu_bg'], (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(surface, COLORS['menu_border'], (menu_x, menu_y, menu_width, menu_height), 2)

        title_text = self.font_small.render(f'{tower.name} Lv.{tower.level}', True, COLORS['text'])
        surface.blit(title_text, (menu_x + 10, menu_y + 8))

        stats_text = self.font_small.render(
            f'DMG:{tower.damage} RNG:{tower.range} SPD:{1 / tower.fire_rate:.1f}/s',
            True, (200, 200, 200))
        surface.blit(stats_text, (menu_x + 10, menu_y + 28))

        btn_rect = pygame.Rect(menu_x + 10, menu_y + 60, 180, 40)

        if tower.can_upgrade():
            upgrade_cost = tower.get_upgrade_cost()
            can_afford = economy.can_afford(upgrade_cost)

            if hovered_btn and can_afford:
                pygame.draw.rect(surface, COLORS['button_hover'], btn_rect)
            elif not can_afford:
                pygame.draw.rect(surface, COLORS['upgrade_disabled'], btn_rect)
            else:
                pygame.draw.rect(surface, COLORS['upgrade_button'], btn_rect)

            btn_color = (255, 255, 255) if can_afford else (150, 150, 150)
            upgrade_text = self.font_medium.render(f'Upgrade ${upgrade_cost}', True, btn_color)
        else:
            pygame.draw.rect(surface, COLORS['upgrade_disabled'], btn_rect)
            upgrade_text = self.font_medium.render('Max Level', True, (200, 200, 200))

        text_rect = upgrade_text.get_rect(center=btn_rect.center)
        surface.blit(upgrade_text, text_rect)

    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOP_UI_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, TOP_UI_HEIGHT))

        pause_text = self.font_large.render('PAUSED', True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(pause_text, pause_rect)

        hint_text = self.font_small.render('Press SPACE to resume', True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        surface.blit(hint_text, hint_rect)

    def draw_end_screen(self, surface, message, color):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        text = self.font_large.render(message, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        surface.blit(text, text_rect)

        restart_text = self.font_medium.render('Click to restart', True, COLORS['text'])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        surface.blit(restart_text, restart_rect)

    def get_place_menu_position(self, mouse_x, mouse_y):
        menu_width = 200
        menu_height = 10 + len(TOWER_TYPES) * 55 + 10
        mx, my = mouse_x, mouse_y
        if mx + menu_width > SCREEN_WIDTH:
            mx = SCREEN_WIDTH - menu_width
        if my + menu_height > SCREEN_HEIGHT:
            my = SCREEN_HEIGHT - menu_height
        return (mx, my)

    def get_upgrade_menu_position(self, mouse_x, mouse_y):
        menu_width = 200
        menu_height = 110
        mx, my = mouse_x, mouse_y
        if mx + menu_width > SCREEN_WIDTH:
            mx = SCREEN_WIDTH - menu_width
        if my + menu_height > SCREEN_HEIGHT:
            my = SCREEN_HEIGHT - menu_height
        return (mx, my)

    def is_place_menu_button_clicked(self, mouse_x, mouse_y, menu_x, menu_y):
        tower_types = list(TOWER_TYPES.keys())
        for i, tower_type in enumerate(tower_types):
            btn_y = menu_y + 10 + i * 55
            btn_rect = pygame.Rect(menu_x + 10, btn_y, 180, 45)
            if btn_rect.collidepoint(mouse_x, mouse_y):
                return tower_type
        return None

    def is_upgrade_button_clicked(self, mouse_x, mouse_y, menu_x, menu_y):
        btn_rect = pygame.Rect(menu_x + 10, menu_y + 60, 180, 40)
        return btn_rect.collidepoint(mouse_x, mouse_y)
