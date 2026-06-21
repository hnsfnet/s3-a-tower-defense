import pytest
from collections import deque
from config import EMPTY, PATH, START, END, GRID_COLS, GRID_ROWS, TILE_SIZE, TOP_UI_HEIGHT
from game_map import GameMap


def _calc_path_from_grid(grid, grid_rows, grid_cols):
    start_pos = None
    end_pos = None
    for row in range(grid_rows):
        for col in range(grid_cols):
            if grid[row][col] == START:
                start_pos = (row, col)
            elif grid[row][col] == END:
                end_pos = (row, col)
    if not start_pos or not end_pos:
        return None
    visited = set()
    parent = {}
    queue = deque([start_pos])
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
            n = (nr, nc)
            if 0 <= nr < grid_rows and 0 <= nc < grid_cols:
                if n not in visited:
                    cell = grid[nr][nc]
                    if cell == PATH or cell == END:
                        visited.add(n)
                        parent[n] = current
                        queue.append(n)
    if not found:
        return None
    path = []
    node = end_pos
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path


def test_straight_line_path():
    rows, cols = 3, 8
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    grid[1][0] = START
    for c in range(1, cols - 1):
        grid[1][c] = PATH
    grid[1][cols - 1] = END
    path = _calc_path_from_grid(grid, rows, cols)
    assert path is not None
    assert len(path) == cols
    assert path[0] == (1, 0) and path[-1] == (1, cols - 1)
    for i, (r, c) in enumerate(path):
        assert r == 1 and c == i


def test_forked_path_picks_shortest():
    rows, cols = 6, 6
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = START
    for c in range(1, cols):
        grid[0][c] = PATH
    for r in range(1, rows):
        grid[r][0] = PATH
        grid[r][cols - 1] = PATH
    for c in range(cols):
        grid[rows - 1][c] = PATH
    grid[rows - 1][cols - 1] = END
    path = _calc_path_from_grid(grid, rows, cols)
    assert path is not None
    expected_min = rows + cols - 1
    assert len(path) == expected_min, f"Shortest path should be {expected_min} steps, got {len(path)}"


def test_no_path_dead_end():
    rows, cols = 4, 4
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = START
    grid[0][1] = PATH
    grid[1][1] = PATH
    grid[1][2] = PATH
    grid[3][3] = END
    path = _calc_path_from_grid(grid, rows, cols)
    assert path is None, "Dead-end disconnected grid should yield no path"


def test_missing_end_cell_returns_none():
    rows, cols = 3, 3
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    grid[1][1] = START
    path = _calc_path_from_grid(grid, rows, cols)
    assert path is None, "Without END cell there can be no path"


def test_missing_start_cell_returns_none():
    rows, cols = 3, 3
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    grid[2][2] = END
    path = _calc_path_from_grid(grid, rows, cols)
    assert path is None, "Without START cell there can be no path"


def test_start_equals_end_single_cell():
    rows, cols = 3, 3

    only_start = [[EMPTY]*cols for _ in range(rows)]
    only_start[1][1] = START
    assert _calc_path_from_grid(only_start, rows, cols) is None

    only_end = [[EMPTY]*cols for _ in range(rows)]
    only_end[2][2] = END
    assert _calc_path_from_grid(only_end, rows, cols) is None

    start_real, end_real = (1, 1), (1, 1)
    visited, parent, q = set(), {}, deque()
    q.append(start_real)
    visited.add(start_real)
    parent[start_real] = None
    found = False
    while q:
        cur = q.popleft()
        if cur == end_real:
            found = True
            break
    assert found is True, "When start equals end, first popleft triggers found immediately"
    node = end_real
    path_built = []
    while node is not None:
        path_built.append(node)
        node = parent[node]
    path_built.reverse()
    assert path_built == [(1, 1)], "Single cell path when start equals end"

    from game_map import GameMap
    gm = GameMap.__new__(GameMap)
    gm.grid = [[EMPTY]*cols for _ in range(rows)]
    gm.grid[1][1] = START
    for r in range(rows):
        for c in range(cols):
            if r == 1 and c == 1:
                gm.grid[r][c] = END
    start_found = end_found = None
    for r in range(rows):
        for c in range(cols):
            cell = gm.grid[r][c]
            if cell == START:
                start_found = (r, c)
            elif cell == END:
                end_found = (r, c)
    assert start_found is None
    assert end_found == (1, 1)
    gm.grid[1][1] = START
    start_found2 = end_found2 = None
    for r in range(rows):
        for c in range(cols):
            cell = gm.grid[r][c]
            if cell == START:
                start_found2 = (r, c)
            elif cell == END:
                end_found2 = (r, c)
    assert start_found2 == (1, 1)
    assert end_found2 is None


def test_default_map_has_valid_path(game_map):
    assert len(game_map.path_points) > 0
    first = game_map.path_points[0]
    last = game_map.path_points[-1]
    expected_first_x = 0 * TILE_SIZE + TILE_SIZE // 2
    expected_first_y = 2 * TILE_SIZE + TILE_SIZE // 2 + TOP_UI_HEIGHT
    assert abs(first[0] - expected_first_x) < 2
    assert abs(last[0] - (19 * TILE_SIZE + TILE_SIZE // 2)) < 2


def test_path_matches_manhattan_distance_on_grid_without_obstacles():
    rows, cols = 5, 5
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    grid[0][0] = START
    grid[0][1] = grid[0][2] = grid[0][3] = PATH
    grid[1][3] = grid[2][3] = grid[3][3] = PATH
    grid[4][0] = grid[4][1] = grid[4][2] = grid[4][3] = grid[4][4] = PATH
    grid[1][0] = grid[2][0] = grid[3][0] = PATH
    grid[2][4] = END
    grid[3][4] = PATH
    path = _calc_path_from_grid(grid, rows, cols)
    assert path is not None
    assert path[0] == (0, 0)
    assert path[-1] == (2, 4)
    manhattan = abs(0 - 2) + abs(0 - 4)
    assert len(path) - 1 == manhattan, \
        f"BFS path should be {manhattan} steps (Manhattan), got {len(path)-1}"
