import math
from config import *


class Projectile:
    def __init__(self, x, y, target, damage, splash=False, splash_radius=0):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.splash = splash
        self.splash_radius = splash_radius
        self.speed = 300
        self.active = True
        self.size = 4

    def update(self, dt, enemies):
        if not self.active:
            return []

        if not self.target or not self.target.alive:
            self.active = False
            return []

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 8:
            self.active = False
            return self._deal_damage(enemies)

        move_dist = self.speed * dt
        ratio = move_dist / dist
        self.x += dx * ratio
        self.y += dy * ratio

        return []

    def _deal_damage(self, enemies):
        killed_rewards = []

        if self.splash:
            for enemy in enemies:
                if not enemy.alive:
                    continue
                dx = enemy.x - self.target.x
                dy = enemy.y - self.target.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= self.splash_radius:
                    if enemy.take_damage(self.damage):
                        killed_rewards.append(enemy.reward)
        else:
            if self.target.alive:
                if self.target.take_damage(self.damage):
                    killed_rewards.append(self.target.reward)

        return killed_rewards

    def draw(self, surface):
        if not self.active:
            return

        if self.splash:
            pygame.draw.circle(surface, COLORS['projectile'], (int(self.x), int(self.y)), self.size + 2)
        else:
            pygame.draw.circle(surface, COLORS['projectile'], (int(self.x), int(self.y)), self.size)


class Explosion:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_radius = radius
        self.duration = 0.3
        self.timer = self.duration
        self.active = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return

        alpha = int(255 * (self.timer / self.duration))
        color = list(COLORS['explosion'])
        radius = int(self.radius * (1 - self.timer / self.duration * 0.5))
        surf = pygame.Surface((self.max_radius * 2, self.max_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (color[0], color[1], color[2], alpha),
                         (self.max_radius, self.max_radius), radius)
        surface.blit(surf, (int(self.x - self.max_radius), int(self.y - self.max_radius)))


class Tower:
    def __init__(self, grid_col, grid_row, tower_type):
        self.grid_col = grid_col
        self.grid_row = grid_row
        self.x = grid_col * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_row * TILE_SIZE + TILE_SIZE // 2 + TOP_UI_HEIGHT
        self.tower_type = tower_type
        stats = TOWER_TYPES[tower_type]
        self.name = stats['name']
        self.damage = stats['damage']
        self.range = stats['range']
        self.fire_rate = stats['fire_rate']
        self.cost = stats['cost']
        self.color = stats['color']
        self.splash = stats['splash']
        self.splash_radius = stats['splash_radius']
        self.fire_timer = 0
        self.size = 16

    def update(self, dt, enemies, projectiles, explosions):
        self.fire_timer -= dt

        if self.fire_timer > 0:
            return []

        target = self._find_target(enemies)
        if target:
            self.fire_timer = self.fire_rate
            proj = Projectile(
                self.x, self.y,
                target,
                self.damage,
                self.splash,
                self.splash_radius
            )
            projectiles.append(proj)
            return []

        return []

    def _find_target(self, enemies):
        best_target = None
        best_progress = -1

        for enemy in enemies:
            if not enemy.alive:
                continue

            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)

            if dist <= self.range:
                progress = enemy.path_index
                if progress > best_progress:
                    best_progress = progress
                    best_target = enemy

        return best_target

    def draw(self, surface, show_range=False):
        if show_range:
            pygame.draw.circle(surface, COLORS['range_circle'], (int(self.x), int(self.y)), int(self.range), 1)

        pygame.draw.rect(
            surface,
            self.color,
            (int(self.x - self.size), int(self.y - self.size),
            self.size * 2, self.size * 2)
        )

        if self.splash:
            pygame.draw.circle(surface, (50, 50, 50), (int(self.x), int(self.y)), 6)
        else:
            pygame.draw.rect(surface, (50, 50, 50), (int(self.x - 2), int(self.y - self.size - 4), 4, 10))

    def draw_range(self, surface):
        pygame.draw.circle(surface, COLORS['range_circle'], (int(self.x), int(self.y)), int(self.range), 1)
