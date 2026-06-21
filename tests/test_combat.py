import pytest
import math
from config import TOWER_TYPES, TILE_SIZE, TOP_UI_HEIGHT, COLORS


def _dist(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


def test_single_tower_picks_furthest_enemy(make_tower, make_enemy):
    arrow = make_tower('arrow')
    arrow.x, arrow.y = 400, 300
    arrow.range = 300

    enemies = [
        make_enemy(), make_enemy(), make_enemy(),
    ]
    enemies[0].x, enemies[0].y = 420, 310; enemies[0].path_index = 1
    enemies[1].x, enemies[1].y = 500, 300; enemies[1].path_index = 5
    enemies[2].x, enemies[2].y = 480, 300; enemies[2].path_index = 8

    target = arrow._find_target(enemies)
    assert target is enemies[2], f"Should pick furthest (path_index=8), got path_index={target.path_index}"


def test_out_of_range_not_selected(make_tower, make_enemy):
    arrow = make_tower('arrow')
    arrow.x, arrow.y = 400, 300
    arrow.range = 50

    e_near = make_enemy(); e_near.x, e_near.y = 430, 300; e_near.path_index = 3
    e_far = make_enemy(); e_far.x, e_far.y = 600, 300; e_far.path_index = 999

    target = arrow._find_target([e_near, e_far])
    assert target is e_near, f"Should only pick in-range enemy"

    target2 = arrow._find_target([e_far])
    assert target2 is None, "No in-range enemy should return None"


def test_aoe_tower_picks_densest_area(make_tower, make_enemy):
    cannon = make_tower('cannon')
    cannon.x, cannon.y = 400, 300
    cannon.range = 300
    cannon.splash_radius = 60

    enemies = []
    cluster_center = (450, 300)
    for i in range(4):
        e = make_enemy()
        e.x = cluster_center[0] + i * 10
        e.y = cluster_center[1]
        e.path_index = 3 + i
        enemies.append(e)

    lone = make_enemy()
    lone.x, lone.y = 550, 300
    lone.path_index = 100
    enemies.append(lone)

    target = cannon._find_target(enemies)
    assert target is not None
    dx = target.x - cluster_center[0]
    dy = target.y - cluster_center[1]
    assert math.sqrt(dx * dx + dy * dy) <= 40, \
        f"AOE target should be near cluster center, got ({target.x}, {target.y})"

    hits = 0
    for e in enemies:
        if math.sqrt((e.x - target.x) ** 2 + (e.y - target.y) ** 2) <= cannon.splash_radius:
            hits += 1
    assert hits >= 4, f"Should hit at least 4 enemies in splash, got {hits}"


def test_splash_damages_multiple_enemies(make_tower, make_enemy):
    cannon = make_tower('cannon')
    cannon.x, cannon.y = 400, 300
    cannon.splash_radius = 60

    target = make_enemy(hp=200); target.x, target.y = 440, 300
    splash1 = make_enemy(hp=200); splash1.x, splash1.y = 460, 300
    splash2 = make_enemy(hp=200); splash2.x, splash2.y = 420, 300
    safe = make_enemy(hp=200); safe.x, safe.y = 700, 300

    from tower import Projectile
    p = Projectile(cannon.x, cannon.y, target, 50, attack_type='splash',
                   splash=True, splash_radius=60)
    p.x, p.y = target.x, target.y
    rewards = p._deal_damage([target, splash1, splash2, safe])

    assert target.hp == 150, "Primary target should take full damage"
    assert splash1.hp == 150 and splash2.hp == 150, "Enemies in splash should take damage"
    assert safe.hp == 200, "Enemies out of splash must not take damage"


def test_slow_effect_numeric_and_duration(make_tower, make_enemy):
    e = make_enemy(hp=100, speed=60)
    base_speed = e.base_speed
    assert e.get_current_speed() == base_speed

    e.apply_slow(0.5, 2.0)
    assert abs(e.get_current_speed() - base_speed * 0.5) < 0.01, "Slow should cut speed by 50%"

    e.update(1.0)
    assert abs(e.get_current_speed() - base_speed * 0.5) < 0.01, "Slow should persist for 2s"

    e.update(1.1)
    assert abs(e.get_current_speed() - base_speed) < 0.01, "Slow should expire after 2.1s > 2.0s"


def test_ice_projectile_applies_slow(make_tower, make_enemy):
    ice = make_tower('ice')
    ice.x, ice.y = 400, 300
    e = make_enemy(hp=200, speed=60)
    e.x, e.y = 440, 300
    base_speed = e.base_speed

    from tower import Projectile
    p = Projectile(ice.x, ice.y, e, 10, attack_type='slow',
                   slow_percent=0.5, slow_duration=2.0,
                   color=COLORS.get('ice_projectile', (120, 200, 255)))
    p.x, p.y = e.x, e.y
    p._deal_damage([e])

    assert e.hp == 190
    assert abs(e.get_current_speed() - base_speed * 0.5) < 0.01


def test_chain_lightning_decays_damage(make_tower, make_enemy):
    lt = make_tower('lightning')
    lt.x, lt.y = 400, 300
    lt.chain_count = 3
    lt.chain_damage_decay = 0.7
    lt.damage = 100
    lt.range = 400

    enemies = []
    positions = [(430, 300), (460, 300), (490, 300)]
    for i, (px, py) in enumerate(positions):
        e = make_enemy(hp=1000)
        e.x, e.y = px, py
        enemies.append(e)

    effects = []
    rewards = lt._chain_attack(enemies[0], enemies, effects)

    assert len(effects) == 1, "Should produce lightning visual effect"
    dmg_expected = [100, 70, 49]
    for i, exp in enumerate(dmg_expected):
        actual = 1000 - enemies[i].hp
        assert abs(actual - exp) < 0.01, \
            f"Chain enemy {i}: expected {exp} damage, got {actual}"


def test_chain_lightning_stops_at_range(make_tower, make_enemy):
    lt = make_tower('lightning')
    lt.x, lt.y = 400, 300
    lt.chain_count = 3
    lt.chain_damage_decay = 0.7
    lt.damage = 100
    lt.range = 200

    close = make_enemy(hp=1000); close.x, close.y = 430, 300
    far = make_enemy(hp=1000); far.x, far.y = 9000, 9000
    enemies = [close, far]

    rewards = lt._chain_attack(close, enemies, [])
    assert close.hp < 1000
    assert far.hp == 1000, "Out of chain range enemy should be untouched"


def test_kill_yields_reward(make_enemy):
    e = make_enemy(hp=50, reward=123)
    killed = e.take_damage(1000)
    assert killed is True
    assert e.reward == 123
    assert e.alive is False


def test_combat_system_cleanup(make_enemy, systems):
    combat = systems['combat']
    enemies = [make_enemy() for _ in range(5)]
    for e in enemies[:3]:
        e.take_damage(999999)
    alive = combat.cleanup_dead_enemies(enemies)
    assert len(alive) == 2
    for e in alive:
        assert e.alive is True
