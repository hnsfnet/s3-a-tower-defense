import pytest
from config import INITIAL_GOLD, INITIAL_LIVES, TOWER_TYPES, MAX_TOWER_LEVEL


def test_initial_gold_and_lives(systems):
    eco = systems['economy']
    assert eco.gold == INITIAL_GOLD
    assert eco.lives == INITIAL_LIVES
    assert eco.is_game_over() is False


def test_place_tower_deducts_gold(systems):
    eco = systems['economy']
    game_map = systems['map']
    cost = TOWER_TYPES['arrow']['cost']

    ok, reason = eco.can_place_tower('arrow', game_map, 3, 3, [])
    assert ok is True and reason == 'ok'

    before = eco.gold
    tower = eco.place_tower('arrow', 3, 3)
    assert tower is not None
    assert eco.gold == before - cost
    assert tower.tower_type == 'arrow'
    assert tower.level == 1


def test_cannot_place_with_no_gold(systems):
    eco = systems['economy']
    game_map = systems['map']
    eco.gold = 1
    ok, reason = eco.can_place_tower('cannon', game_map, 3, 3, [])
    assert ok is False and reason == 'no_gold'
    before = eco.gold
    t = eco.place_tower('cannon', 3, 3)
    assert t is None
    assert eco.gold == before


def test_cannot_place_on_path_or_occupied(systems):
    eco = systems['economy']
    game_map = systems['map']
    existing = []
    first = eco.place_tower('arrow', 3, 3)
    existing.append(first)

    ok2, reason2 = eco.can_place_tower('arrow', game_map, 3, 3, existing)
    assert ok2 is False and reason2 == 'occupied'

    ok3, reason3 = eco.can_place_tower('arrow', game_map, 0, 2, existing)
    assert ok3 is False and reason3 == 'not_placeable'


def test_kill_adds_gold(systems):
    eco = systems['economy']
    before = eco.gold
    eco.add_gold(42)
    assert eco.gold == before + 42

    rewards = [10, 20, 30]
    for r in rewards:
        eco.add_gold(r)
    assert eco.gold == before + 42 + 60


def test_deduct_life(systems):
    eco = systems['economy']
    for _ in range(INITIAL_LIVES - 1):
        eco.deduct_life()
    assert eco.lives == 1
    assert eco.is_game_over() is False
    eco.deduct_life()
    assert eco.lives == 0
    assert eco.is_game_over() is True
    eco.deduct_life()
    assert eco.lives == 0, "Lives should not go below 0"


def test_upgrade_cost_increases(systems, make_tower):
    eco = systems['economy']
    tower = make_tower('arrow', 0, 0)
    costs = []
    for _ in range(MAX_TOWER_LEVEL - 1):
        costs.append(tower.get_upgrade_cost())
        eco.upgrade_tower(tower)
    assert len(costs) == MAX_TOWER_LEVEL - 1
    assert all(c > 0 for c in costs), "Each upgrade should cost > 0"
    if len(costs) >= 2:
        assert costs[-1] > costs[0], "Higher level upgrades should cost more"


def test_max_level_upgrade_refuses_no_gold_deducted(systems, make_tower):
    eco = systems['economy']
    tower = make_tower('arrow', 0, 0)
    for _ in range(MAX_TOWER_LEVEL - 1):
        eco.upgrade_tower(tower)
    assert tower.level == MAX_TOWER_LEVEL

    before = eco.gold
    res = eco.can_upgrade_tower(tower)
    assert res is False

    done = eco.upgrade_tower(tower)
    assert done is False
    assert eco.gold == before, "No gold should be deducted for max-level upgrade"


def test_sell_refunds_50_percent(systems, make_tower):
    eco = systems['economy']
    cost = TOWER_TYPES['arrow']['cost']
    start_gold = eco.gold

    tower = eco.place_tower('arrow', 3, 3)
    assert eco.gold == start_gold - cost

    refund = eco.sell_tower(tower)
    expected_refund = tower.get_total_invested() // 2
    assert refund == expected_refund
    assert eco.gold == start_gold - cost + expected_refund


def test_sell_after_upgrades_returns_50_percent_total_invested(systems, make_tower):
    eco = systems['economy']
    tower = make_tower('arrow', 3, 3)
    eco.gold = 99999

    placed_cost = TOWER_TYPES['arrow']['cost']
    eco.gold -= placed_cost

    upgrade_sum = 0
    for _ in range(MAX_TOWER_LEVEL - 1):
        upgrade_sum += tower.get_upgrade_cost()
        eco.upgrade_tower(tower)

    total_invested = placed_cost + upgrade_sum
    assert tower.get_total_invested() == total_invested
    expected_refund = int(total_invested * 0.5)

    before_sell = eco.gold
    refund = eco.sell_tower(tower)
    assert refund == expected_refund
    assert eco.gold == before_sell + expected_refund


def test_reset_restores_initial_values(systems):
    eco = systems['economy']
    eco.gold = 1
    eco.lives = 0
    eco.reset()
    assert eco.gold == INITIAL_GOLD
    assert eco.lives == INITIAL_LIVES
