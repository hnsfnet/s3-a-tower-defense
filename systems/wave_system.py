from wave_manager import WaveManager


class WaveSystem:
    def __init__(self, path_points):
        self.manager = WaveManager(path_points)

    def update(self, dt, enemies):
        self.manager.update(dt, enemies)

    def start_wave(self):
        self.manager.start_wave()

    def check_and_end_wave(self, enemies):
        if self.manager.is_wave_complete(enemies):
            self.manager.end_wave()
            return True
        return False

    def is_game_won(self):
        return self.manager.is_game_won()

    def can_start_next_wave(self):
        return self.manager.can_start_next_wave()

    def get_cooldown_remaining(self):
        return self.manager.get_cooldown_remaining()

    @property
    def current_wave(self):
        return self.manager.current_wave

    @property
    def total_waves(self):
        return self.manager.total_waves

    @property
    def in_cooldown(self):
        return self.manager.in_cooldown

    @property
    def wave_active(self):
        return self.manager.wave_active

    def get_remaining_enemies(self, enemies):
        return self.manager.get_remaining_enemies(enemies)
