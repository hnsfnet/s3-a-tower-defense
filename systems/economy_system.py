from config import *
from tower import Tower


class EconomySystem:
    def __init__(self):
        self.gold = INITIAL_GOLD
        self.lives = INITIAL_LIVES

    def add_gold(self, amount):
        self.gold += amount

    def deduct_life(self):
        if self.lives > 0:
            self.lives -= 1
        return self.lives

    def can_afford(self, cost):
        return self.gold >= cost

    def can_place_tower(self, tower_type, game_map, grid_col, grid_row, existing_towers):
        if not game_map.is_placeable(grid_col, grid_row):
            return False, 'not_placeable'
        for tower in existing_towers:
            if tower.grid_col == grid_col and tower.grid_row == grid_row:
                return False, 'occupied'
        cost = TOWER_TYPES[tower_type]['cost']
        if not self.can_afford(cost):
            return False, 'no_gold'
        return True, 'ok'

    def place_tower(self, tower_type, grid_col, grid_row):
        cost = TOWER_TYPES[tower_type]['cost']
        if not self.can_afford(cost):
            return None
        tower = Tower(grid_col, grid_row, tower_type)
        self.gold -= cost
        return tower

    def can_upgrade_tower(self, tower):
        if not tower.can_upgrade():
            return False
        cost = tower.get_upgrade_cost()
        return self.can_afford(cost)

    def upgrade_tower(self, tower):
        if not self.can_upgrade_tower(tower):
            return False
        cost = tower.get_upgrade_cost()
        if tower.upgrade():
            self.gold -= cost
            return True
        return False

    def sell_tower(self, tower, refund_ratio=0.5):
        refund = tower.get_sell_refund(refund_ratio)
        self.gold += refund
        return refund

    def is_game_over(self):
        return self.lives <= 0

    def reset(self):
        self.gold = INITIAL_GOLD
        self.lives = INITIAL_LIVES
