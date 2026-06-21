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

COLORS = {
    'background': (30, 30, 30),
    'empty': (60, 120, 60),
    'path': (180, 140, 80),
    'start': (50, 200, 50),
    'end': (200, 50, 50),
    'grid_line': (40, 40, 40),
    'ui_bg': (50, 50, 50),
    'text': (255, 255, 255),
    'enemy': (200, 50, 50),
    'enemy_hp_bar_bg': (80, 0, 0),
    'enemy_hp_bar': (0, 200, 0),
    'arrow_tower': (100, 100, 255),
    'cannon_tower': (255, 100, 50),
    'projectile': (255, 255, 100),
    'explosion': (255, 150, 50),
    'range_circle': (255, 255, 255),
    'menu_bg': (70, 70, 70),
    'menu_border': (200, 200, 200),
    'button_hover': (100, 100, 100),
}

TOWER_TYPES = {
    'arrow': {
        'name': 'Arrow Tower',
        'damage': 15,
        'range': 120,
        'fire_rate': 0.5,
        'cost': 50,
        'color': COLORS['arrow_tower'],
        'splash': False,
        'splash_radius': 0,
    },
    'cannon': {
        'name': 'Cannon Tower',
        'damage': 40,
        'range': 90,
        'fire_rate': 1.5,
        'cost': 100,
        'color': COLORS['cannon_tower'],
        'splash': True,
        'splash_radius': 50,
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
