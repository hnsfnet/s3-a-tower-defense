import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')

import pygame
from config import INITIAL_GOLD, INITIAL_LIVES, TOTAL_WAVES, WAVE_COOLDOWN


def _create_game():
    import main
    return main.Game()


def test_boot_state_is_menu():
    g = _create_game()
    assert g.state == 'menu'


def test_menu_to_playing_on_any_click():
    g = _create_game()
    g.state = 'menu'
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                            pos=(g.screen.get_width() // 2, g.screen.get_height() // 2))
    g._handle_menu_event(ev)
    assert g.state == 'playing'
    assert g.paused is False


def test_pause_toggle_via_space_key():
    g = _create_game()
    g.state = 'playing'
    g.paused = False
    ev_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    g._handle_game_event(ev_down)
    assert g.paused is True
    g._handle_game_event(ev_down)
    assert g.paused is False


def test_speed_toggle_via_f_key():
    g = _create_game()
    g.state = 'playing'
    assert g.speed_multiplier == 1
    ev_f = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)
    g._handle_game_event(ev_f)
    assert g.speed_multiplier == 2
    g._handle_game_event(ev_f)
    assert g.speed_multiplier == 1


def test_start_next_wave_on_enter():
    g = _create_game()
    g.state = 'playing'
    assert g.wave_system.current_wave == 0
    ev_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    g._handle_game_event(ev_enter)
    assert g.wave_system.current_wave == 1
    assert g.wave_system.wave_active is True


def test_game_over_loses():
    g = _create_game()
    g.state = 'playing'
    for _ in range(INITIAL_LIVES):
        g.economy.deduct_life()
    g._update(0.01)
    assert g.state == 'lost'
    assert g.economy.is_game_over() is True


def test_victory_after_all_waves():
    g = _create_game()
    g.state = 'playing'
    g.economy.gold = 99999

    for wave_num in range(1, TOTAL_WAVES + 1):
        g.wave_system.start_wave()
        for _ in range(10000):
            g.wave_system.update(0.1, g.enemies)
            if len(g.wave_system.manager.wave_spawn_queue) == 0:
                break
        for e in g.enemies:
            e.alive = False
        g.wave_system.check_and_end_wave(g.enemies)
        for _ in range(int(WAVE_COOLDOWN * 2) + 1):
            g.wave_system.update(1.0, [])

    g._update(0.01)
    assert g.state == 'won', f"Expected won, got {g.state}"
    assert g.wave_system.is_game_won() is True


def test_restart_from_lost_resets_game():
    g = _create_game()
    g.state = 'playing'
    g.economy.gold = 0
    g.economy.lives = 0
    g.paused = True
    g.speed_multiplier = 2
    from tower import Tower
    g.towers.append(Tower(3, 3, 'arrow'))
    g.state = 'lost'

    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
    g._handle_end_event(ev)
    assert g.state == 'menu'
    assert g.economy.gold == INITIAL_GOLD
    assert g.economy.lives == INITIAL_LIVES
    assert len(g.towers) == 0
    assert len(g.enemies) == 0
    assert g.speed_multiplier == 1
    assert g.paused is False


def test_restart_from_won_resets_game():
    g = _create_game()
    g.state = 'playing'
    from tower import Tower
    g.towers.append(Tower(3, 3, 'arrow'))
    g.state = 'won'

    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))
    g._handle_end_event(ev)
    assert g.state == 'menu'
    assert len(g.towers) == 0
    assert g.economy.gold == INITIAL_GOLD
    assert g.speed_multiplier == 1
    assert g.paused is False


def test_full_transition_chain():
    g = _create_game()

    assert g.state == 'menu'

    start_ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                  pos=(g.screen.get_width() // 2, g.screen.get_height() // 2))
    g._handle_menu_event(start_ev)
    assert g.state == 'playing'

    space = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    g._handle_game_event(space)
    assert g.paused is True
    g._handle_game_event(space)
    assert g.paused is False

    for _ in range(INITIAL_LIVES):
        g.economy.deduct_life()
    g._update(0.01)
    assert g.state == 'lost'

    restart_ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5))
    g._handle_end_event(restart_ev)
    assert g.state == 'menu'
    assert g.economy.lives == INITIAL_LIVES
    assert g.economy.gold == INITIAL_GOLD

    g._handle_menu_event(start_ev)
    assert g.state == 'playing'
