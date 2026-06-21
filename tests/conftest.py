import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
import pytest
from config import TILE_SIZE, TOP_UI_HEIGHT, TOWER_TYPES, COLORS
from game_map import GameMap
from enemy import Enemy
from tower import Tower
from systems import CombatSystem, WaveSystem, EconomySystem, RenderSystem
from ui_renderer import UIRenderer


@pytest.fixture(autouse=True, scope='session')
def _init_pygame_headless():
    pygame.init()
    dummy_surface = pygame.display.set_mode((10, 10))
    yield
    pygame.quit()


@pytest.fixture
def game_map():
    return GameMap()


@pytest.fixture
def straight_path_points():
    points = []
    for x in range(10):
        px = x * TILE_SIZE + TILE_SIZE // 2
        py = TILE_SIZE // 2 + TOP_UI_HEIGHT
        points.append((px, py))
    return points


@pytest.fixture
def make_enemy(straight_path_points):
    def _make(hp=100, speed=60, reward=10, size=14, etype='normal', wave=1, path=None):
        p = path if path is not None else straight_path_points
        if etype == 'from_config':
            return Enemy.create(p, wave, 'normal')
        return Enemy(p, hp, speed, reward, size, etype)
    return _make


@pytest.fixture
def make_tower():
    def _make(tower_type='arrow', grid_col=5, grid_row=5, x=None, y=None):
        t = Tower(grid_col, grid_row, tower_type)
        if x is not None:
            t.x = x
        if y is not None:
            t.y = y
        return t
    return _make


@pytest.fixture
def systems(game_map):
    ui = UIRenderer()
    combat = CombatSystem()
    economy = EconomySystem()
    wave = WaveSystem(game_map.path_points)
    render = RenderSystem(ui)
    return {
        'combat': combat,
        'economy': economy,
        'wave': wave,
        'render': render,
        'ui': ui,
        'map': game_map,
    }
