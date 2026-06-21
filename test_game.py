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


def test_enemy_types(game_map):
    print("=== Testing Enemy Types ===")

    for enemy_type in ['normal', 'fast', 'boss']:
        enemy = Enemy.create(game_map.path_points, wave=1, enemy_type=enemy_type)
        print(f"{enemy_type}: HP={enemy.max_hp}, Speed={enemy.base_speed}, "
              f"Reward={enemy.reward}, Size={enemy.size}")
    print()

    print("Testing slow effect:")
    normal = Enemy.create(game_map.path_points, wave=1, enemy_type='normal')
    original_speed = normal.base_speed
    normal.apply_slow(0.5, 2.0)
    current_speed = normal.get_current_speed()
    print(f"Original speed: {original_speed}, Slowed speed: {current_speed}")
    assert abs(current_speed - original_speed * 0.5) < 0.01, "Slow effect not working"

    normal.update(3.0)
    speed_after = normal.get_current_speed()
    print(f"Speed after 3 seconds: {speed_after}")
    assert abs(speed_after - original_speed) < 0.01, "Slow should have expired"

    print("Enemy types test passed!\n")


def test_tower_types_and_upgrades(game_map):
    print("=== Testing Tower Types & Upgrades ===")

    tower_types = ['arrow', 'cannon', 'ice', 'lightning']
    for t_type in tower_types:
        tower = Tower(1, 1, t_type)
        print(f"\n{tower.name} (Level 1):")
        print(f"  Damage: {tower.damage}, Range: {tower.range}, Fire rate: {tower.fire_rate}s")
        print(f"  Size: {tower.size}, Attack type: {tower.attack_type}")

        while tower.can_upgrade():
            cost = tower.get_upgrade_cost()
            success = tower.upgrade()
            assert success, "Upgrade should succeed"
            print(f"  -> Level {tower.level}: Damage={tower.damage}, "
                  f"Range={tower.range}, Size={tower.size}")

        assert not tower.can_upgrade(), "Should reach max level"
        assert tower.level == MAX_TOWER_LEVEL, f"Should be level {MAX_TOWER_LEVEL}"

    print("\nTower types & upgrades test passed!\n")


def test_wave_manager_mixed(game_map):
    print("=== Testing Wave Manager (Mixed Enemies) ===")
    wm = WaveManager(game_map.path_points)
    print(f"Total waves: {wm.total_waves}")

    for wave in range(1, min(6, wm.total_waves + 1)):
        enemies = []
        wm.start_wave()
        queue = list(wm.wave_spawn_queue)
        normal = queue.count('normal')
        fast = queue.count('fast')
        boss = queue.count('boss')
        print(f"Wave {wave}: {normal} normal, {fast} fast, {boss} boss (total: {len(queue)})")

        for i in range(100):
            wm.update(0.5, enemies)
            if len(wm.wave_spawn_queue) == 0:
                break
        print(f"  Spawned: {wm.enemies_spawned} enemies")

    print("Wave manager (mixed) test passed!\n")


def test_projectile_types(game_map):
    print("=== Testing Projectile Types ===")

    print("Testing slow projectile:")
    enemy = Enemy.create(game_map.path_points, wave=1, enemy_type='normal')
    enemy.x = 200
    enemy.y = 200
    original_speed = enemy.base_speed

    proj = Projectile(100, 200, enemy, damage=10, attack_type='slow',
                     slow_percent=0.5, slow_duration=2.0)
    enemies = [enemy]
    for i in range(200):
        proj.update(0.01, enemies)
        if not proj.active:
            break

    print(f"  HP after hit: {enemy.hp}")
    assert enemy.hp == 90, "Should have 90 HP left"
    slowed_speed = enemy.get_current_speed()
    print(f"  Speed after hit: {slowed_speed}")
    assert abs(slowed_speed - original_speed * 0.5) < 0.01, "Slow not applied"

    print("\nProjectile types test passed!\n")


if __name__ == '__main__':
    print("=" * 50)
    print("Starting Tower Defense v2 Module Tests")
    print("=" * 50 + "\n")

    try:
        game_map = test_game_map()
        test_enemy_types(game_map)
        test_tower_types_and_upgrades(game_map)
        test_wave_manager_mixed(game_map)
        test_projectile_types(game_map)
        print("=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
