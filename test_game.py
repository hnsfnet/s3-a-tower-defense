import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))

from config import *
from game_map import GameMap
from enemy import Enemy
from tower import Tower
from systems import CombatSystem, WaveSystem, EconomySystem


def test_json_config_loaded():
    print("=== Testing JSON Config Loading ===")
    print(f"Tower types loaded: {list(TOWER_TYPES.keys())}")
    print(f"Enemy types loaded: {list(ENEMY_TYPES.keys())}")
    print(f"Wave cooldown: {WAVE_COOLDOWN}, Boss interval: {BOSS_WAVE_INTERVAL}")

    for t_name, t_data in TOWER_TYPES.items():
        assert 'name' in t_data, f"Tower {t_name} missing 'name'"
        assert 'levels' in t_data, f"Tower {t_name} missing 'levels'"
        assert 'base_color' in t_data, f"Tower {t_name} missing 'base_color'"
        assert len(t_data['levels']) == MAX_TOWER_LEVEL, \
            f"Tower {t_name} should have {MAX_TOWER_LEVEL} levels, got {len(t_data['levels'])}"
        print(f"  {t_data['name']}: ${t_data['cost']}, lv1 DMG={t_data['levels'][0]['damage']}")

    for e_name, e_data in ENEMY_TYPES.items():
        assert 'hp_multiplier' in e_data, f"Enemy {e_name} missing hp_multiplier"
        assert 'color' in e_data, f"Enemy {e_name} missing color"

    print("JSON config test passed!\n")


def test_game_map():
    print("=== Testing Game Map ===")
    game_map = GameMap()
    print(f"Path points: {len(game_map.path_points)}")
    assert len(game_map.path_points) > 0, "Path calculation failed"
    print("Map module test passed!\n")
    return game_map


def test_shortest_path():
    print("=== Testing Shortest Path ===")
    from collections import deque

    class FakeMap:
        def __init__(self, grid):
            self.grid = grid
            self.path_cells = []
            self._calc()

        def _calc(self):
            start_pos = end_pos = None
            for row in range(len(self.grid)):
                for col in range(len(self.grid[0])):
                    if self.grid[row][col] == START:
                        start_pos = (row, col)
                    elif self.grid[row][col] == END:
                        end_pos = (row, col)
            if not start_pos or not end_pos:
                return
            visited, parent, queue = set(), {}, deque()
            queue.append(start_pos)
            visited.add(start_pos)
            parent[start_pos] = None
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            found = False
            while queue:
                current = queue.popleft()
                if current == end_pos:
                    found = True
                    break
                row, col = current
                for dr, dc in directions:
                    nr, nc = row + dr, col + dc
                    neighbor = (nr, nc)
                    if 0 <= nr < len(self.grid) and 0 <= nc < len(self.grid[0]):
                        if neighbor not in visited:
                            cell = self.grid[nr][nc]
                            if cell == PATH or cell == END:
                                visited.add(neighbor)
                                parent[neighbor] = current
                                queue.append(neighbor)
            if not found:
                return
            path = []
            node = end_pos
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            self.path_cells = path

    long_grid = [
        [START, PATH, PATH, PATH, PATH, END],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PATH],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PATH],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PATH],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, PATH],
    ]
    fm = FakeMap(long_grid)
    print(f"Path length: {len(fm.path_cells)}, expected 6")
    assert len(fm.path_cells) == 6, "Shortest path incorrect"
    print("Shortest path test passed!\n")


def test_aoe_targeting():
    print("=== Testing AOE Targeting ===")
    path_points = [(100, 100), (200, 100), (300, 100), (400, 100)]
    cannon = Tower(0, 0, 'cannon')
    cannon.x, cannon.y = 250, 100
    cannon.range = 200
    cannon.splash_radius = 50

    enemies = []
    positions = [(230, 2), (250, 3), (270, 1), (400, 5)]
    for (px, pidx) in positions:
        e = Enemy(path_points, 100, 60, 10, 14, 'normal')
        e.x, e.y = px, 100
        e.path_index = pidx
        enemies.append(e)

    target = cannon._find_target(enemies)
    hit_count = 0
    for e in enemies:
        dx, dy = e.x - target.x, e.y - target.y
        if math.sqrt(dx * dx + dy * dy) <= cannon.splash_radius:
            hit_count += 1
    print(f"AOE target: ({target.x}, {target.y}), splash hits: {hit_count}")
    assert hit_count >= 3, f"AOE should hit 3 enemies, got {hit_count}"

    arrow = Tower(0, 0, 'arrow')
    arrow.x, arrow.y = 250, 100
    arrow.range = 200
    single_target = arrow._find_target(enemies)
    print(f"Single target path_index: {single_target.path_index}, expected 5")
    assert single_target.path_index == 5, "Single tower should pick furthest enemy"
    print("AOE targeting test passed!\n")


def test_economy_system():
    print("=== Testing Economy System ===")
    game_map = GameMap()
    eco = EconomySystem()
    print(f"Initial gold: {eco.gold}, lives: {eco.lives}")
    assert eco.gold == INITIAL_GOLD, f"Gold should be {INITIAL_GOLD}"
    assert eco.lives == INITIAL_LIVES, f"Lives should be {INITIAL_LIVES}"

    result, reason = eco.can_place_tower('arrow', game_map, 3, 3, [])
    print(f"Can place arrow tower at (3,3): {result}, reason: {reason}")
    assert result is True, "Should be able to place arrow tower on empty tile"

    tower = eco.place_tower('arrow', 3, 3)
    print(f"After placing: gold={eco.gold}, tower exists={tower is not None}")
    assert tower is not None, "Tower should be created"
    assert eco.gold == INITIAL_GOLD - TOWER_TYPES['arrow']['cost'], "Gold should be deducted"

    for _ in range(MAX_TOWER_LEVEL - 1):
        upgraded = eco.upgrade_tower(tower)
        print(f"  Upgrade to Lv.{tower.level}: {'OK' if upgraded else 'FAIL'}, gold={eco.gold}")
    assert tower.level == MAX_TOWER_LEVEL, f"Should be at max level {MAX_TOWER_LEVEL}"

    upgraded = eco.upgrade_tower(tower)
    print(f"Upgrade at max level: {'OK' if upgraded else 'FAIL (correct)'}")
    assert not upgraded, "Should fail at max level"

    eco.add_gold(50)
    eco.deduct_life()
    print(f"After +50 gold, -1 life: gold={eco.gold}, lives={eco.lives}")
    assert eco.lives == INITIAL_LIVES - 1

    eco.reset()
    print(f"After reset: gold={eco.gold}, lives={eco.lives}")
    assert eco.gold == INITIAL_GOLD
    assert eco.lives == INITIAL_LIVES

    print("Economy system test passed!\n")


def test_combat_system():
    print("=== Testing Combat System ===")
    path_points = [(100, 100), (200, 100), (300, 100)]
    combat = CombatSystem()
    enemies = []
    for i in range(3):
        e = Enemy(path_points, 100, 60, 10, 14, 'normal')
        e.x, e.y, e.path_index = 100 + i * 50, 100, i
        enemies.append(e)

    combat.update_enemies(0.5, enemies)
    print(f"Enemies after 0.5s: {[(int(e.x), int(e.y)) for e in enemies]}")
    assert all(e.alive for e in enemies), "All should be alive"

    for e in enemies:
        e.take_damage(9999)
    enemies = combat.cleanup_dead_enemies(enemies)
    print(f"After cleanup: alive enemies = {len(enemies)}")
    assert len(enemies) == 0, "All should be dead and removed"

    print("Combat system test passed!\n")


def test_wave_system():
    print("=== Testing Wave System ===")
    game_map = GameMap()
    ws = WaveSystem(game_map.path_points)
    print(f"Total waves: {ws.total_waves}, can start: {ws.can_start_next_wave()}")
    assert ws.can_start_next_wave() is True, "Should be able to start first wave"

    ws.start_wave()
    print(f"Wave {ws.current_wave} started, active: {ws.wave_active}")
    assert ws.current_wave == 1
    assert ws.wave_active is True

    enemies = []
    for i in range(200):
        ws.update(0.5, enemies)
        if len(ws.manager.wave_spawn_queue) == 0:
            break
    print(f"Spawned: {ws.manager.enemies_spawned} enemies")

    for e in enemies:
        e.alive = False
    assert ws.check_and_end_wave(enemies) is True, "Wave should end"
    assert ws.in_cooldown is True, "Should be in cooldown"
    print(f"In cooldown: {ws.in_cooldown}, remaining: {ws.get_cooldown_remaining():.1f}s")

    assert ws.can_start_next_wave() is False, "Cannot start during cooldown"

    for i in range(int(WAVE_COOLDOWN * 2) + 1):
        ws.update(1.0, [])
    print(f"Cooldown expired: in_cooldown={ws.in_cooldown}, can_start={ws.can_start_next_wave()}")
    assert ws.can_start_next_wave() is True, "Should be able to start after cooldown"

    print("Wave system test passed!\n")


def test_enemy_types():
    print("=== Testing Enemy Types ===")
    game_map = GameMap()
    for etype in ['normal', 'fast', 'boss']:
        e = Enemy.create(game_map.path_points, wave=1, enemy_type=etype)
        print(f"  {etype}: HP={e.max_hp}, Speed={e.base_speed}, "
              f"Reward={e.reward}, Size={e.size}")
    normal = Enemy.create(game_map.path_points, wave=1, enemy_type='normal')
    normal.apply_slow(0.5, 2.0)
    slowed = normal.get_current_speed()
    original = normal.base_speed
    print(f"Slow test: original={original}, slowed={slowed}")
    assert abs(slowed - original * 0.5) < 0.01, "Slow effect not applied"
    normal.update(3.0)
    assert abs(normal.get_current_speed() - original) < 0.01, "Slow should expire"
    print("Enemy types test passed!\n")


if __name__ == '__main__':
    print("=" * 55)
    print(" Refactored Tower Defense - Full Regression Tests")
    print("=" * 55 + "\n")

    try:
        test_json_config_loaded()
        test_game_map()
        test_shortest_path()
        test_aoe_targeting()
        test_economy_system()
        test_combat_system()
        test_wave_system()
        test_enemy_types()
        print("=" * 55)
        print(" ALL REFACTOR TESTS PASSED!")
        print("=" * 55)
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
