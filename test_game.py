import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import *
from game_map import GameMap
from enemy import Enemy
from tower import Tower, Projectile
from wave_manager import WaveManager


def test_game_map():
    print("=== Testing Game Map ===")
    game_map = GameMap()
    print(f"Grid size: {GRID_COLS} x {GRID_ROWS}")
    print(f"Path points: {len(game_map.path_points)}")

    start_found = False
    end_found = False
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if game_map.grid[row][col] == START:
                start_found = True
                print(f"Start position: ({col}, {row})")
            elif game_map.grid[row][col] == END:
                end_found = True
                print(f"End position: ({col}, {row})")

    assert start_found, "Start not found"
    assert end_found, "End not found"
    assert len(game_map.path_points) > 0, "Path calculation failed"
    print("Map module test passed!\n")
    return game_map


def test_enemy(game_map):
    print("=== Testing Enemy ===")
    enemy = Enemy(game_map.path_points, hp=100, speed=50, reward=10)
    print(f"Enemy start position: ({enemy.x}, {enemy.y})")
    print(f"Enemy HP: {enemy.hp}/{enemy.max_hp}")

    enemy.update(0.1)
    print(f"Position after update: ({enemy.x}, {enemy.y})")

    killed = enemy.take_damage(50)
    print(f"After 50 damage: HP={enemy.hp}, Killed={killed}")
    assert not killed, "Should not be dead"

    killed = enemy.take_damage(50)
    print(f"After another 50 damage: HP={enemy.hp}, Killed={killed}")
    assert killed, "Should be dead"
    assert not enemy.alive, "Enemy should be marked as dead"

    print("Enemy module test passed!\n")


def test_tower(game_map):
    print("=== Testing Tower ===")
    arrow_tower = Tower(1, 1, 'arrow')
    print(f"Arrow tower position: ({arrow_tower.x}, {arrow_tower.y})")
    print(f"Arrow tower damage: {arrow_tower.damage}")
    print(f"Arrow tower range: {arrow_tower.range}")
    print(f"Arrow tower fire rate: {arrow_tower.fire_rate}s")

    cannon_tower = Tower(2, 2, 'cannon')
    print(f"Cannon tower damage: {cannon_tower.damage}")
    print(f"Cannon tower splash: {cannon_tower.splash}, radius: {cannon_tower.splash_radius}")

    enemies = []
    projectiles = []
    explosions = []
    arrow_tower.update(0.1, enemies, projectiles, explosions)
    print(f"Projectiles with no enemies: {len(projectiles)}")

    print("Tower module test passed!\n")


def test_wave_manager(game_map):
    print("=== Testing Wave Manager ===")
    wm = WaveManager(game_map.path_points)
    print(f"Total waves: {wm.total_waves}")
    print(f"Current wave: {wm.current_wave}")

    enemies = []
    wm.start_wave()
    print(f"Starting wave 1, enemy count: {wm.enemies_per_wave}")
    assert wm.wave_active == True, "Wave should be active"

    for i in range(20):
        wm.update(0.5, enemies)
    print(f"Spawned enemies: {wm.enemies_spawned}")
    print(f"Enemies on field: {len(enemies)}")

    print("Wave manager test passed!\n")


def test_projectile(game_map):
    print("=== Testing Projectile ===")
    enemy = Enemy(game_map.path_points, hp=100, speed=0, reward=10)
    enemy.x = 200
    enemy.y = 200

    proj = Projectile(100, 200, enemy, damage=30)
    print(f"Projectile start position: ({proj.x}, {proj.y})")

    enemies = [enemy]
    for i in range(100):
        rewards = proj.update(0.01, enemies)
        if not proj.active:
            break

    print(f"Enemy HP after hit: {enemy.hp}")
    assert enemy.hp == 70, f"Should have 70 HP left, got {enemy.hp}"
    print("Projectile test passed!\n")


if __name__ == '__main__':
    print("Starting tower defense game module tests...\n")

    try:
        game_map = test_game_map()
        test_enemy(game_map)
        test_tower(game_map)
        test_wave_manager(game_map)
        test_projectile(game_map)
        print("✅ All tests passed!")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
