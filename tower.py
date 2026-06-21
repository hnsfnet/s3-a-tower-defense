import math
from config import *


class LightningEffect:
    def __init__(self, points):
        self.points = points
        self.duration = 0.2
        self.timer = self.duration
        self.active = True

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i + 1]
            pygame.draw.line(surface,
                           COLORS['lightning'],
                           (int(start[0]), int(start[1])),
                           (int(end[0]), int(end[1])), 3)
            pygame.draw.line(surface,
                           (255, 255, 255),
                           (int(start[0]), int(start[1])),
                           (int(end[0]), int(end[1])), 1)


class Projectile:
    def __init__(self, x, y, target, damage, attack_type='single',
                 splash=False, splash_radius=0, slow_percent=0, slow_duration=0,
                 color=COLORS['projectile']):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.attack_type = attack_type
        self.splash = splash
        self.splash_radius = splash_radius
        self.slow_percent = slow_percent
        self.slow_duration = slow_duration
        self.speed = 350
        self.active = True
        self.size = 4
        self.color = color

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

        if self.attack_type == 'slow':
            if self.target.alive:
                self.target.apply_slow(self.slow_percent, self.slow_duration)
                if self.target.take_damage(self.damage):
                    killed_rewards.append(self.target.reward)
        elif self.splash:
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

        if self.splash or self.attack_type == 'slow':
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size + 2)
        else:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


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

        config = TOWER_TYPES[tower_type]
        self.name = config['name']
        self.base_color = config['base_color']
        self.projectile_color = config['projectile_color']
        self.attack_type = config['attack_type']
        self.cost = config['cost']

        self.splash_radius = config.get('splash_radius', 0)
        self.slow_percent = config.get('slow_percent', 0)
        self.slow_duration = config.get('slow_duration', 0)
        self.chain_count = config.get('chain_count', 0)
        self.chain_damage_decay = config.get('chain_damage_decay', 0)

        self.level = 1
        self.fire_timer = 0
        self._apply_level_stats()

    def _apply_level_stats(self):
        level_data = TOWER_TYPES[self.tower_type]['levels'][self.level - 1]
        self.damage = level_data['damage']
        self.range = level_data['range']
        self.fire_rate = level_data['fire_rate']
        self.size = level_data['size']
        self.upgrade_cost = level_data['upgrade_cost']
        self.color = get_tower_level_color(self.base_color, self.level)

    def can_upgrade(self):
        return self.level < MAX_TOWER_LEVEL

    def get_upgrade_cost(self):
        if self.can_upgrade():
            return self.upgrade_cost
        return 0

    def upgrade(self):
        if not self.can_upgrade():
            return False
        self.level += 1
        self._apply_level_stats()
        return True

    def get_total_invested(self):
        total = self.cost
        for lv in range(1, self.level):
            total += TOWER_TYPES[self.tower_type]['levels'][lv - 1]['upgrade_cost']
        return total

    def get_sell_refund(self, refund_ratio=0.5):
        return int(self.get_total_invested() * refund_ratio)

    def update(self, dt, enemies, projectiles, effects):
        self.fire_timer -= dt

        if self.fire_timer > 0:
            return []

        target = self._find_target(enemies)
        if not target:
            return []

        self.fire_timer = self.fire_rate

        if self.attack_type == 'chain':
            return self._chain_attack(target, enemies, effects)
        else:
            proj = Projectile(
                self.x, self.y,
                target,
                self.damage,
                attack_type=self.attack_type,
                splash=(self.attack_type == 'splash'),
                splash_radius=self.splash_radius,
                slow_percent=self.slow_percent,
                slow_duration=self.slow_duration,
                color=self.projectile_color,
            )
            projectiles.append(proj)
            return []

    def _chain_attack(self, primary_target, enemies, effects):
        killed_rewards = []
        hit_enemies = set()
        lightning_points = [(self.x, self.y)]

        current_target = primary_target
        current_damage = self.damage

        for chain_idx in range(self.chain_count):
            if not current_target or not current_target.alive:
                break
            if current_target in hit_enemies:
                break

            hit_enemies.add(current_target)
            lightning_points.append((current_target.x, current_target.y))

            if current_target.take_damage(current_damage):
                killed_rewards.append(current_target.reward)

            if self.attack_type == 'slow' and self.slow_percent > 0:
                current_target.apply_slow(self.slow_percent, self.slow_duration)

            current_damage = current_damage * self.chain_damage_decay

            next_target = None
            min_dist = float('inf')
            for enemy in enemies:
                if enemy.alive and enemy not in hit_enemies:
                    dx = enemy.x - current_target.x
                    dy = enemy.y - current_target.y
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist <= self.range * 0.8 and dist < min_dist:
                        min_dist = dist
                        next_target = enemy

            current_target = next_target

        effect = LightningEffect(lightning_points)
        effects.append(effect)

        return killed_rewards

    def _find_target(self, enemies):
        in_range = []
        for enemy in enemies:
            if not enemy.alive:
                continue
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= self.range:
                in_range.append(enemy)

        if not in_range:
            return None

        if self.attack_type == 'splash':
            return self._find_best_aoe_target(in_range, enemies)

        best_target = None
        best_progress = -1
        for enemy in in_range:
            progress = enemy.path_index
            if progress > best_progress:
                best_progress = progress
                best_target = enemy
        return best_target

    def _find_best_aoe_target(self, in_range_enemies, all_enemies):
        best_target = None
        best_hit_count = 0
        best_progress = -1

        for candidate in in_range_enemies:
            hit_count = 0
            for enemy in all_enemies:
                if not enemy.alive:
                    continue
                dx = enemy.x - candidate.x
                dy = enemy.y - candidate.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist <= self.splash_radius:
                    hit_count += 1

            if hit_count > best_hit_count:
                best_hit_count = hit_count
                best_target = candidate
                best_progress = candidate.path_index
            elif hit_count == best_hit_count and best_hit_count > 0:
                if candidate.path_index > best_progress:
                    best_target = candidate
                    best_progress = candidate.path_index

        if best_target is None and in_range_enemies:
            best_target = in_range_enemies[0]
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

        if self.attack_type == 'splash':
            pygame.draw.circle(surface, (50, 50, 50), (int(self.x), int(self.y)), max(4, self.size // 3))
        elif self.attack_type == 'slow':
            pygame.draw.circle(surface, (200, 240, 255), (int(self.x), int(self.y)), max(4, self.size // 3))
        elif self.attack_type == 'chain':
            pygame.draw.line(surface, (255, 255, 100),
                           (int(self.x - self.size // 2), int(self.y - self.size // 2)),
                           (int(self.x + self.size // 2), int(self.y + self.size // 2)), 2)
            pygame.draw.line(surface, (255, 255, 100),
                           (int(self.x + self.size // 2), int(self.y - self.size // 2)),
                           (int(self.x - self.size // 2), int(self.y + self.size // 2)), 2)
        else:
            pygame.draw.rect(surface, (50, 50, 50),
                           (int(self.x - 2), int(self.y - self.size - 4), 4, max(6, self.size // 2)))

        if self.level > 1:
            for i in range(self.level - 1):
                pygame.draw.circle(surface, (255, 215, 0),
                               (int(self.x - 8 + i * 8), int(self.y + self.size + 6)), 3)

    def draw_range(self, surface):
        pygame.draw.circle(surface, COLORS['range_circle'], (int(self.x), int(self.y)), int(self.range), 1)
