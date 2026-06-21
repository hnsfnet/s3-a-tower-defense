import math
from config import *


class Enemy:
    def __init__(self, path_points, hp, speed, reward):
        self.path_points = path_points
        self.path_index = 0
        self.x = path_points[0][0]
        self.y = path_points[0][1] + TOP_UI_HEIGHT - TILE_SIZE // 2
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.reward = reward
        self.size = ENEMY_BASE_STATS['size']
        self.reached_end = False
        self.alive = True

    def update(self, dt):
        if not self.alive or self.reached_end:
            return

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

        move_speed = self.speed * dt
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

        pygame.draw.circle(surface, COLORS['enemy'], (int(self.x), int(self.y)), self.size)

        bar_width = 28
        bar_height = 4
        bar_x = self.x - bar_width / 2
        bar_y = self.y - self.size - 8

        pygame.draw.rect(surface, COLORS['enemy_hp_bar_bg'], (bar_x, bar_y, bar_width, bar_height))

        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, COLORS['enemy_hp_bar'], (bar_x, bar_y, bar_width * hp_ratio, bar_height))
