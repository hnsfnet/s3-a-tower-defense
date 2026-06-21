TILE_SIZE = 40
GRID_COLS = 20
GRID_ROWS = 15
SCREEN_WIDTH = TILE_SIZE * GRID_COLS
SCREEN_HEIGHT = TILE_SIZE * GRID_ROWS + 80
TOP_UI_HEIGHT = 80

FPS = 60

EMPTY = 0
PATH = 1
START = 2
END = 3

MAX_TOWER_LEVEL = 3

COLORS = {
    'background': (30, 30, 30),
    'empty': (60, 120, 60),
    'path': (180, 140, 80),
    'start': (50, 200, 50),
    'end': (200, 50, 50),
    'grid_line': (40, 40, 40),
    'ui_bg': (50, 50, 50),
    'text': (255, 255, 255),
    'enemy_normal': (200, 50, 50),
    'enemy_fast': (255, 200, 50),
    'enemy_boss': (150, 0, 150),
    'enemy_hp_bar_bg': (80, 0, 0),
    'enemy_hp_bar': (0, 200, 0),
    'enemy_slow': (100, 200, 255),
    'arrow_tower': (100, 100, 255),
    'cannon_tower': (255, 100, 50),
    'ice_tower': (100, 200, 255),
    'lightning_tower': (255, 255, 100),
    'projectile': (255, 255, 100),
    'ice_projectile': (150, 230, 255),
    'lightning': (255, 255, 50),
    'explosion': (255, 150, 50),
    'range_circle': (255, 255, 255),
    'menu_bg': (70, 70, 70),
    'menu_border': (200, 200, 200),
    'button_hover': (100, 100, 100),
    'upgrade_button': (50, 150, 50),
    'upgrade_disabled': (80, 80, 80),
}


def _darken_color(color, amount=30):
    return (max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount))


def _get_tower_level_color(base_color, level):
    return _darken_color(base_color, (level - 1) * 25)


TOWER_TYPES = {
    'arrow': {
        'name': 'Arrow Tower',
        'cost': 50,
        'base_color': COLORS['arrow_tower'],
        'projectile_color': COLORS['projectile'],
        'attack_type': 'single',
        'levels': [
            {'damage': 15, 'range': 120, 'fire_rate': 0.5, 'size': 14, 'upgrade_cost': 60},
            {'damage': 25, 'range': 140, 'fire_rate': 0.4, 'size': 16, 'upgrade_cost': 100},
            {'damage': 40, 'range': 160, 'fire_rate': 0.3, 'size': 18, 'upgrade_cost': 0},
        ],
    },
    'cannon': {
        'name': 'Cannon Tower',
        'cost': 100,
        'base_color': COLORS['cannon_tower'],
        'projectile_color': COLORS['projectile'],
        'attack_type': 'splash',
        'splash_radius': 50,
        'levels': [
            {'damage': 40, 'range': 90, 'fire_rate': 1.5, 'size': 16, 'upgrade_cost': 100},
            {'damage': 70, 'range': 105, 'fire_rate': 1.3, 'size': 18, 'upgrade_cost': 160},
            {'damage': 110, 'range': 120, 'fire_rate': 1.1, 'size': 20, 'upgrade_cost': 0},
        ],
    },
    'ice': {
        'name': 'Ice Tower',
        'cost': 75,
        'base_color': COLORS['ice_tower'],
        'projectile_color': COLORS['ice_projectile'],
        'attack_type': 'slow',
        'slow_percent': 0.5,
        'slow_duration': 2.0,
        'levels': [
            {'damage': 8, 'range': 110, 'fire_rate': 0.7, 'size': 14, 'upgrade_cost': 80},
            {'damage': 14, 'range': 125, 'fire_rate': 0.6, 'size': 16, 'upgrade_cost': 130},
            {'damage': 22, 'range': 140, 'fire_rate': 0.5, 'size': 18, 'upgrade_cost': 0},
        ],
    },
    'lightning': {
        'name': 'Lightning Tower',
        'cost': 125,
        'base_color': COLORS['lightning_tower'],
        'projectile_color': COLORS['lightning'],
        'attack_type': 'chain',
        'chain_count': 3,
        'chain_damage_decay': 0.7,
        'levels': [
            {'damage': 25, 'range': 130, 'fire_rate': 1.0, 'size': 15, 'upgrade_cost': 120},
            {'damage': 40, 'range': 150, 'fire_rate': 0.9, 'size': 17, 'upgrade_cost': 180},
            {'damage': 65, 'range': 170, 'fire_rate': 0.7, 'size': 19, 'upgrade_cost': 0},
        ],
    },
}


ENEMY_TYPES = {
    'normal': {
        'name': 'Normal',
        'hp_multiplier': 1.0,
        'speed_multiplier': 1.0,
        'reward_multiplier': 1.0,
        'size_multiplier': 1.0,
        'color': COLORS['enemy_normal'],
    },
    'fast': {
        'name': 'Fast',
        'hp_multiplier': 0.5,
        'speed_multiplier': 2.0,
        'reward_multiplier': 1.2,
        'size_multiplier': 0.8,
        'color': COLORS['enemy_fast'],
    },
    'boss': {
        'name': 'Boss',
        'hp_multiplier': 10.0,
        'speed_multiplier': 0.6,
        'reward_multiplier': 5.0,
        'size_multiplier': 1.8,
        'color': COLORS['enemy_boss'],
    },
}

ENEMY_BASE_STATS = {
    'hp': 100,
    'speed': 60,
    'reward': 15,
    'size': 14,
}

INITIAL_GOLD = 200
INITIAL_LIVES = 20
TOTAL_WAVES = 10

WAVE_ENEMY_BASE = 5
WAVE_ENEMY_INCREMENT = 3
WAVE_HP_MULTIPLIER = 1.2
WAVE_SPAWN_INTERVAL = 1.0
WAVE_COOLDOWN = 3.0
BOSS_WAVE_INTERVAL = 5
