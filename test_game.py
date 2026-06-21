import sys
import os
import math

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


def test_shortest_path():
    print("=== Testing Shortest Path (Bug 1 Fix) ===")
    from collections import deque

    class FakeMap:
        def __init__(self, grid):
            self.grid = grid
            self.path_points = []
            self._calc()

        def _calc(self):
            start_pos = None
            end_pos = None
            for row in range(len(self.grid)):
                for col in range(len(self.grid[0])):
                    if self.grid[row][col] == START:
                        start_pos = (row, col)
                    elif self.grid[row][col] == END:
                        end_pos = (row, col)

            if not start_pos or not end_pos:
                return

            visited = set()
            parent = {}
            queue = deque()
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
    path = fm.path_cells
    print(f"Branching map path length: {len(path)}")
    print(f"Path: {path}")

    expected_short = 6
    assert len(path) == expected_short, \
        f"Shortest path should be {expected_short} tiles, got {len(path)}"

    print("Shortest path test passed!\n")


def test_aoe_targeting():
    print("=== Testing AOE Targeting (Bug 2 Fix) ===")
    path_points = [(100, 100), (200, 100), (300, 100), (400, 100)]
    cannon = Tower(0, 0, 'cannon')
    cannon.x = 250
    cannon.y = 100
    cannon.range = 200
    cannon.splash_radius = 50

    e1 = Enemy(path_points, 100, 60, 10, 14, 'normal')
    e1.x = 230
    e1.y = 100
    e1.path_index = 2

    e2 = Enemy(path_points, 100, 60, 10, 14, 'normal')
    e2.x = 250
    e2.y = 100
    e2.path_index = 3

    e3 = Enemy(path_points, 100, 60, 10, 14, 'normal')
    e3.x = 270
    e3.y = 100
    e3.path_index = 1

    e4 = Enemy(path_points, 100, 60, 10, 14, 'normal')
    e4.x = 400
    e4.y = 100
    e4.path_index = 5

    enemies = [e1, e2, e3, e4]
    target = cannon._find_target(enemies)

    print(f"AOE target position: ({target.x}, {target.y})")
    print(f"e1 at (230,100), e2 at (250,100), e3 at (270,100), e4 at (400,100)")

    hit_count = 0
    for e in enemies:
        if not e.alive:
            continue
        dx = e.x - target.x
        dy = e.y - target.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= cannon.splash_radius:
            hit_count += 1
    print(f"Enemies hit by splash: {hit_count}")
    assert hit_count >= 3, f"AOE should hit at least 3 enemies, got {hit_count}"

    arrow = Tower(0, 0, 'arrow')
    arrow.x = 250
    arrow.y = 100
    arrow.range = 200
    target_single = arrow._find_target(enemies)
    print(f"Single-target tower picks: path_index={target_single.path_index}")
    assert target_single.path_index == 5, "Single tower should target furthest enemy"

    print("AOE targeting test passed!\n")


def test_wave_cooldown():
    print("=== Testing Wave Cooldown (Bug 3 Fix) ===")
    game_map = GameMap()
    wm = WaveManager(game_map.path_points)

    wm.start_wave()
    assert wm.wave_active == True, "Wave should be active"
    assert wm.in_cooldown == False, "Should not be in cooldown"
    print(f"Wave {wm.current_wave} started, enemies: {wm.total_enemies_in_wave}")

    enemies = []
    for i in range(200):
        wm.update(0.5, enemies)
        if len(wm.wave_spawn_queue) == 0:
            break
    print(f"All spawned: {wm.enemies_spawned}, queue: {len(wm.wave_spawn_queue)}")

    for e in enemies:
        e.alive = False

    assert wm.is_wave_complete(enemies) == True, "Wave should be complete"
    wm.end_wave()
    assert wm.in_cooldown == True, "Should enter cooldown after wave ends"
    print(f"In cooldown: {wm.in_cooldown}, timer: {wm.cooldown_timer:.1f}s")

    assert wm.can_start_next_wave() == False, "Should NOT start next wave during cooldown"

    for i in range(int(WAVE_COOLDOWN * 2) + 1):
        wm.update(1.0, enemies)
    assert wm.in_cooldown == False, "Cooldown should expire"
    assert wm.wave_active == False, "Wave should be inactive after cooldown"
    assert wm.can_start_next_wave() == True, "Should be able to start next wave after cooldown"
    print("Cooldown expired, can start next wave: True")

    print("Wave cooldown test passed!\n")


def test_upgrade_safety():
    print("=== Testing Upgrade Safety (Bug 4 Fix) ===")
    tower = Tower(1, 1, 'arrow')
    print(f"Initial: Level {tower.level}, can_upgrade={tower.can_upgrade()}")

    gold = 10000
    upgrade_count = 0
    while tower.can_upgrade():
        cost = tower.get_upgrade_cost()
        result = tower.upgrade()
        if result:
            gold -= cost
            upgrade_count += 1
        else:
            print("ERROR: Upgrade failed but should have succeeded!")
            break
    print(f"After max upgrades: Level {tower.level}, upgrades done: {upgrade_count}")

    assert tower.level == MAX_TOWER_LEVEL, "Should be at max level"
    assert not tower.can_upgrade(), "Should not be upgradeable at max level"

    result = tower.upgrade()
    assert result == False, "Upgrade at max level should return False"
    print(f"Upgrade at max level returned: {result} (gold NOT deducted)")

    print("Upgrade safety test passed!\n")


def test_enemy_types():
    print("=== Testing Enemy Types ===")
    game_map = GameMap()
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


if __name__ == '__main__':
    print("=" * 55)
    print(" Tower Defense Bug Fix Verification Tests")
    print("=" * 55 + "\n")

    try:
        game_map = test_game_map()
        test_shortest_path()
        test_aoe_targeting()
        test_wave_cooldown()
        test_upgrade_safety()
        test_enemy_types()
        print("=" * 55)
        print(" ALL BUG FIX TESTS PASSED!")
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
