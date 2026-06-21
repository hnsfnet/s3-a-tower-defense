from config import *
from enemy import Enemy


class WaveManager:
    def __init__(self, path_points):
        self.path_points = path_points
        self.current_wave = 0
        self.enemies_spawned = 0
        self.total_enemies_in_wave = 0
        self.wave_spawn_queue = []
        self.spawn_timer = 0
        self.spawn_interval = WAVE_SPAWN_INTERVAL
        self.wave_active = False
        self.total_waves = TOTAL_WAVES
        self.cooldown_timer = 0
        self.in_cooldown = False

    def _generate_wave_queue(self, wave_num):
        queue = []
        base_count = WAVE_ENEMY_BASE + (wave_num - 1) * WAVE_ENEMY_INCREMENT

        is_boss_wave = (wave_num % BOSS_WAVE_INTERVAL == 0)

        if is_boss_wave:
            fast_count = max(2, base_count // 3)
            normal_count = max(2, base_count - fast_count)
        else:
            fast_count = base_count // 3 if wave_num >= 3 else 0
            normal_count = base_count - fast_count

        for _ in range(normal_count):
            queue.append('normal')

        for _ in range(fast_count):
            queue.append('fast')

        if is_boss_wave:
            queue.append('boss')

        return queue

    def start_wave(self):
        if self.current_wave >= self.total_waves:
            return
        if self.in_cooldown:
            return

        self.current_wave += 1
        self.enemies_spawned = 0
        self.wave_spawn_queue = self._generate_wave_queue(self.current_wave)
        self.total_enemies_in_wave = len(self.wave_spawn_queue)
        self.spawn_timer = 0
        self.wave_active = True
        self.in_cooldown = False

    def update(self, dt, enemies):
        if self.in_cooldown:
            self.cooldown_timer -= dt
            if self.cooldown_timer <= 0:
                self.in_cooldown = False
                self.wave_active = False
            return

        if not self.wave_active:
            return

        if len(self.wave_spawn_queue) == 0:
            return

        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self._spawn_next_enemy(enemies)
            if len(self.wave_spawn_queue) > 0 and self.wave_spawn_queue[0] == 'boss':
                self.spawn_timer = self.spawn_interval * 2
            else:
                self.spawn_timer = self.spawn_interval

    def _spawn_next_enemy(self, enemies):
        if len(self.wave_spawn_queue) == 0:
            return

        enemy_type = self.wave_spawn_queue.pop(0)
        enemy = Enemy.create(self.path_points, self.current_wave, enemy_type)
        enemies.append(enemy)
        self.enemies_spawned += 1

    def is_wave_complete(self, enemies):
        if not self.wave_active or self.in_cooldown:
            return False

        if len(self.wave_spawn_queue) > 0:
            return False

        for enemy in enemies:
            if enemy.alive and not enemy.reached_end:
                return False

        return True

    def end_wave(self):
        self.in_cooldown = True
        self.cooldown_timer = WAVE_COOLDOWN

    def can_start_next_wave(self):
        return not self.wave_active and not self.in_cooldown and not self.is_game_won()

    def get_cooldown_remaining(self):
        if self.in_cooldown:
            return self.cooldown_timer
        return 0

    def get_remaining_enemies(self, enemies):
        remaining = len(self.wave_spawn_queue)
        for enemy in enemies:
            if enemy.alive and not enemy.reached_end:
                remaining += 1
        return remaining

    def is_game_won(self):
        return self.current_wave >= self.total_waves and not self.wave_active

    def get_wave_info(self):
        normal = 0
        fast = 0
        boss = 0
        for t in self.wave_spawn_queue:
            if t == 'normal':
                normal += 1
            elif t == 'fast':
                fast += 1
            elif t == 'boss':
                boss += 1
        return normal, fast, boss
