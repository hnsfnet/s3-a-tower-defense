import json
import os

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

INITIAL_GOLD = 200
INITIAL_LIVES = 20


def _load_json(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, 'configs', filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _apply_color_keys(config_dict):
    for key, value in config_dict.items():
        if isinstance(value, dict):
            _apply_color_keys(value)
            for ckey in list(value.keys()):
                if ckey.endswith('_color_key'):
                    color_key = value.pop(ckey)
                    new_key = ckey.replace('_color_key', '_color')
                    value[new_key] = COLORS[color_key]


def load_tower_config():
    data = _load_json('tower_config.json')
    _apply_color_keys(data)
    return data


def load_enemy_config():
    data = _load_json('enemy_config.json')
    _apply_color_keys(data)
    return data


def load_wave_config():
    return _load_json('wave_config.json')


def darken_color(color, amount=30):
    return (max(0, color[0] - amount), max(0, color[1] - amount), max(0, color[2] - amount))


def get_tower_level_color(base_color, level):
    return darken_color(base_color, (level - 1) * 25)


TOWER_TYPES = load_tower_config()
_ENEMY_CFG = load_enemy_config()
ENEMY_BASE_STATS = _ENEMY_CFG['base_stats']
ENEMY_TYPES = _ENEMY_CFG['types']
_WAVE_CFG = load_wave_config()
TOTAL_WAVES = _WAVE_CFG['total_waves']
WAVE_ENEMY_BASE = _WAVE_CFG['enemy_base']
WAVE_ENEMY_INCREMENT = _WAVE_CFG['enemy_increment']
WAVE_HP_MULTIPLIER = _WAVE_CFG['hp_multiplier']
WAVE_SPAWN_INTERVAL = _WAVE_CFG['spawn_interval']
WAVE_COOLDOWN = _WAVE_CFG['cooldown']
BOSS_WAVE_INTERVAL = _WAVE_CFG['boss_wave_interval']
FAST_ENEMY_START_WAVE = _WAVE_CFG['fast_enemy_start_wave']
FAST_ENEMY_RATIO = _WAVE_CFG['fast_enemy_ratio']
BOSS_WAVE_EXTRA_NORMAL = _WAVE_CFG['boss_wave_extra_normal']
BOSS_WAVE_EXTRA_FAST = _WAVE_CFG['boss_wave_extra_fast']
