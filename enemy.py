import math
from config import *


class Enemy:
    def __init__(self, path_points, hp, base_speed, reward, size, enemy_type='normal'):
        self.path_points = path_points
        self.path_index = 0
        self.x = path_points[0][0]
        self.y = path_points[0][1] + TOP_UI_HEIGHT - TILE_SIZE // 2
        self.max_hp = hp
        self.hp = hp
        self.base_speed = base_speed
        self.reward = reward
        self.size = size
        self.reached_end = False
        self.alive = True
        self.enemy_type = enemy_type

        type_stats = ENEMY_TYPES[enemy_type]
        self.color = type_stats['color']

        self.slow_timer = 0
        self.slow_percent = 0

    @classmethod
    def create(cls, path_points, wave, enemy_type='normal'):
        base_stats = ENEMY_BASE_STATS
        type_stats = ENEMY_TYPES[enemy_type]
        wave_multiplier = WAVE_HP_MULTIPLIER ** (wave - 1)

        hp = int(base_stats['hp'] * type_stats['hp_multiplier'] * wave_multiplier)
        speed = base_stats['speed'] * type_stats['speed_multiplier']
        reward = int(base_stats['reward'] * type_stats['reward_multiplier'] * (1 + (wave - 1) * 0.1))
        size = int(base_stats['size'] * type_stats['size_multiplier'])

        return cls(path_points, hp, speed, reward, size, enemy_type)

    def apply_slow(self, slow_percent, duration):
        if slow_percent > self.slow_percent or self.slow_timer <= 0:
            self.slow_percent = slow_percent
            self.slow_timer = duration
        else:
            self.slow_timer = max(self.slow_timer, duration)

    def get_current_speed(self):
        if self.slow_timer > 0:
            return self.base_speed * (1 - self.slow_percent)
        return self.base_speed

    def update(self, dt):
        if not self.alive or self.reached_end:
            return

        if self.slow_timer > 0:
            self.slow_timer -= dt
            if self.slow_timer <= 0:
                self.slow_timer = 0
                self.slow_percent = 0

        if self.path_index >= len(self.path_points) - 1:
            self.reached_end = True
            return

        target_x = self.path_points[self.path_index + 1][0]
        target_y = self.path_points[self.path_index + 1][1] + TOP_UI_HEIGHT - TILE_SIZE // 2

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 2:
            self.path_index += 1
            return

        move_speed = self.get_current_speed() * dt
        if move_speed >= dist:
            self.x = target_x
            self.y = target_y
            self.path_index += 1
        else:
            self.x += (dx / dist) * move_speed
            self.y += (dy / dist) * move_speed

    def take_damage(self, damage):
        if not self.alive:
            return False
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
            return True
        return False

    def get_position(self):
        return (self.x, self.y)

    def draw(self, surface):
        if not self.alive:
            return

        if self.slow_timer > 0:
            pygame.draw.circle(surface, COLORS['enemy_slow'], (int(self.x), int(self.y)), self.size + 3, 2)

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

        bar_width = int(self.size * 2.2)
        bar_height = 4
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.size - 8

        pygame.draw.rect(surface, COLORS['enemy_hp_bar_bg'], (bar_x, bar_y, bar_width, bar_height))

        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, COLORS['enemy_hp_bar'], (bar_x, bar_y, bar_width * hp_ratio, bar_height))

        if self.enemy_type == 'boss':
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.size - 4, 2)
