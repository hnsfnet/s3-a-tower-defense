import pytest
from config import TOTAL_WAVES, BOSS_WAVE_INTERVAL, WAVE_COOLDOWN, FAST_ENEMY_START_WAVE


def test_wave_generation_order(systems):
    ws = systems['wave']
    mgr = ws.manager
    queue1 = mgr._generate_wave_queue(1)
    assert queue1, "Wave 1 queue should be non-empty"
    assert all(t == 'normal' for t in queue1), "Wave 1 should only contain normals"


def test_per_wave_enemy_counts_and_types(systems):
    ws = systems['wave']
    mgr = ws.manager
    for wave in range(1, TOTAL_WAVES + 1):
        q = mgr._generate_wave_queue(wave)
        normals = q.count('normal')
        fasts = q.count('fast')
        bosses = q.count('boss')
        assert normals + fasts + bosses == len(q)

        if wave >= FAST_ENEMY_START_WAVE and wave % BOSS_WAVE_INTERVAL != 0:
            assert fasts > 0, f"Wave {wave} should contain fast enemies"
        else:
            if wave < FAST_ENEMY_START_WAVE:
                assert fasts == 0, f"Wave {wave} should have 0 fasts"

        if wave % BOSS_WAVE_INTERVAL == 0:
            assert bosses == 1, f"Boss wave {wave} should contain exactly 1 boss"
            assert q[-1] == 'boss', "Boss should spawn last in queue"
        else:
            assert bosses == 0, f"Wave {wave} should have 0 bosses"


def test_boss_every_n_waves(systems):
    ws = systems['wave']
    mgr = ws.manager
    for wave in [5, 10]:
        if wave <= TOTAL_WAVES:
            q = mgr._generate_wave_queue(wave)
            assert q[-1] == 'boss', f"Wave {wave} boss last position"
    for wave in [1, 2, 3, 4, 6, 7]:
        q = mgr._generate_wave_queue(wave)
        assert 'boss' not in q, f"Wave {wave} no boss"


def test_next_wave_blocked_until_all_spawned_and_dead(systems):
    ws = systems['wave']
    assert ws.can_start_next_wave() is True

    ws.start_wave()
    assert ws.current_wave == 1
    assert ws.wave_active is True
    assert ws.can_start_next_wave() is False, "Active wave → can't start next"

    enemies = []
    for _ in range(1000):
        ws.update(0.1, enemies)
        if len(ws.manager.wave_spawn_queue) == 0:
            break

    assert ws.wave_active is True
    assert ws.can_start_next_wave() is False, "Alive enemies → can't start next"

    for e in enemies:
        e.alive = False
    ws.check_and_end_wave(enemies)
    assert ws.in_cooldown is True
    assert ws.can_start_next_wave() is False, "Cooldown → can't start next"

    for _ in range(int(WAVE_COOLDOWN * 2) + 1):
        ws.update(1.0, [])
    assert ws.in_cooldown is False
    assert ws.can_start_next_wave() is True, "Cooldown over → ready"


def test_victory_after_last_wave(systems):
    ws = systems['wave']

    for wave_num in range(1, TOTAL_WAVES + 1):
        ws.start_wave()
        enemies = []
        for _ in range(10000):
            ws.update(0.1, enemies)
            if len(ws.manager.wave_spawn_queue) == 0:
                break
        for e in enemies:
            e.alive = False
        ws.check_and_end_wave(enemies)
        for _ in range(int(WAVE_COOLDOWN * 2) + 1):
            ws.update(1.0, [])

    assert ws.is_game_won() is True, f"After {TOTAL_WAVES} waves game should be won"
    assert ws.can_start_next_wave() is False, "No more waves allowed after victory"


def test_enemies_scale_hp_with_wave(game_map):
    from enemy import Enemy
    e1 = Enemy.create(game_map.path_points, wave=1, enemy_type='normal')
    e5 = Enemy.create(game_map.path_points, wave=5, enemy_type='normal')
    assert e5.max_hp > e1.max_hp, "Later waves should have stronger enemies"


def test_cooldown_timer_ticks_down(systems):
    ws = systems['wave']
    ws.manager.in_cooldown = True
    ws.manager.cooldown_timer = WAVE_COOLDOWN
    ws.update(WAVE_COOLDOWN / 2, [])
    remaining = ws.get_cooldown_remaining()
    assert abs(remaining - WAVE_COOLDOWN / 2) < 0.01
    ws.update(WAVE_COOLDOWN, [])
    assert ws.in_cooldown is False
