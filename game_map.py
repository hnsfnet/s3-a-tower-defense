from collections import deque
from config import *


class GameMap:
    def __init__(self):
        self.grid = self._create_default_map()
        self.path_points = self._calculate_path()

    def _create_default_map(self):
        grid = [[EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        path_coords = [
            (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2),
            (5, 3), (5, 4), (5, 5), (5, 6), (5, 7),
            (6, 7), (7, 7), (8, 7), (9, 7), (10, 7),
            (10, 6), (10, 5), (10, 4), (10, 3), (10, 2),
            (11, 2), (12, 2), (13, 2), (14, 2), (15, 2),
            (15, 3), (15, 4), (15, 5), (15, 6), (15, 7), (15, 8), (15, 9), (15, 10),
            (16, 10), (17, 10), (18, 10), (19, 10),
        ]

        for col, row in path_coords:
            grid[row][col] = PATH

        grid[2][0] = START
        grid[10][19] = END

        return grid

    def _calculate_path(self):
        start_pos = None
        end_pos = None

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if self.grid[row][col] == START:
                    start_pos = (row, col)
                elif self.grid[row][col] == END:
                    end_pos = (row, col)

        if not start_pos or not end_pos:
            return []

        visited = set()
        queue = deque()
        queue.append((start_pos, [start_pos]))
        visited.add(start_pos)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while queue:
            (row, col), path = queue.popleft()

            if (row, col) == end_pos:
                pixel_path = []
                for r, c in path:
                    px = c * TILE_SIZE + TILE_SIZE // 2
                    py = r * TILE_SIZE + TILE_SIZE // 2
                    pixel_path.append((px, py))
                return pixel_path

            for dr, dc in directions:
                new_row = row + dr
                new_col = col + dc

                if 0 <= new_row < GRID_ROWS and 0 <= new_col < GRID_COLS:
                    if (new_row, new_col) not in visited:
                        cell = self.grid[new_row][new_col]
                        if cell == PATH or cell == END:
                            visited.add((new_row, new_col))
                            queue.append(((new_row, new_col), path + [(new_row, new_col)]))

        return []

    def is_placeable(self, grid_col, grid_row):
        if 0 <= grid_row < GRID_ROWS and 0 <= grid_col < GRID_COLS:
            return self.grid[grid_row][grid_col] == EMPTY
        return False

    def get_tile_type(self, grid_col, grid_row):
        if 0 <= grid_row < GRID_ROWS and 0 <= grid_col < GRID_COLS:
            return self.grid[grid_row][grid_col]
        return None

    def draw(self, surface):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                tile_type = self.grid[row][col]
                x = col * TILE_SIZE
                y = row * TILE_SIZE + TOP_UI_HEIGHT

                if tile_type == EMPTY:
                    color = COLORS['empty']
                elif tile_type == PATH:
                    color = COLORS['path']
                elif tile_type == START:
                    color = COLORS['start']
                elif tile_type == END:
                    color = COLORS['end']
                else:
                    color = COLORS['empty']

                pygame.draw.rect(surface, color, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(surface, COLORS['grid_line'], (x, y, TILE_SIZE, TILE_SIZE), 1)
