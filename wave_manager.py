from config import *
from enemy import Enemy


class WaveManager:
    def __init__(self, path_points):
        self.path_points = path_points
        self.current_wave = 0
        self.enemies_spawned = 0
        self.enemies_per_wave = 0
        self.spawn_timer = 0
        self.spawn_interval = WAVE_SPAWN_INTERVAL
        self.wave_active = False
        self.total_waves = TOTAL_WAVES

    def start_wave(self):
        if self.current_wave >= self.total_waves:
            return

        self.current_wave += 1
        self.enemies_spawned = 0
        self.enemies_per_wave = WAVE_ENEMY_BASE + (self.current_wave - 1) * WAVE_ENEMY_INCREMENT
        self.spawn_timer = 0
        self.wave_active = True

    def update(self, dt, enemies):
        if not self.wave_active:
            return

        if self.enemies_spawned >= self.enemies_per_wave:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_enemy(enemies)
            self.spawn_timer = self.spawn_interval

    def _spawn_enemy(self, enemies):
        wave_multiplier = WAVE_HP_MULTIPLIER ** (self.current_wave - 1)
        hp = int(ENEMY_BASE_STATS['hp'] * wave_multiplier)
        speed = ENEMY_BASE_STATS['speed']
        reward = int(ENEMY_BASE_STATS['reward'] * (1 + (self.current_wave - 1) * 0.1))

        enemy = Enemy(self.path_points, hp, speed, reward)
        enemies.append(enemy)
        self.enemies_spawned += 1

    def is_wave_complete(self, enemies):
        if not self.wave_active:
            return False

        if self.enemies_spawned < self.enemies_per_wave:
            return False

        for enemy in enemies:
            if enemy.alive and not enemy.reached_end:
                return False

        return True

    def end_wave(self):
        self.wave_active = False

    def get_remaining_enemies(self, enemies):
        remaining = self.enemies_per_wave - self.enemies_spawned
        for enemy in enemies:
            if enemy.alive and not enemy.reached_end:
                remaining += 1
        return remaining

    def is_game_won(self):
        return self.current_wave >= self.total_waves and not self.wave_active
