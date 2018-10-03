#!/usr/bin/env python3


from Game import Game
from Point import Point


def test_starting_checkers():
    game = Game(True, 8, False, True, 1)
    assert len(game.checkers) == 4


def test_starting_score():
    game = Game(True, 8, False, True, 1)
    assert game.score[Game.WHITE] == 2
    assert game.score[Game.BLACK] == 2


def test_starting_occupied_coordinates():
    game = Game(True, 8, False, True, 1)
    assert len(game.occupied_coordinates) == 4


def test_checker_adding():
    game = Game(True, 8, False, True, 1)
    starting_len = len(game.checkers)
    game.add_checker(Point(0, 0), False)
    current_len = len(game.checkers)
    assert current_len - starting_len == 1


def bot_turn_test(bot_level):
    game = Game(True, 4, True, False, bot_level)
    a = game.is_white_turn
    color = Game.WHITE if game.BOT_IS_WHITE else Game.BLACK
    starting_score = game.score[color]
    game.bot_turn()
    current_score = game.score[color]
    return current_score > starting_score


def test_normal_bot_turn():
    assert bot_turn_test(1)


def test_easy_bot_turn():
    assert bot_turn_test(0)


def test_hard_bot_turn():
    assert bot_turn_test(2)


def test_game_finished():
    game = Game(True, 8, False, True, 1)
    assert not game.is_finished


def test_game_map():
    game = Game(True, 8, False, True, 1)
    assert len(game.game_map) == len(game.get_map())


def test_turn():
    game = Game(True, 8, False, True, 1)
    assert game.is_white_turn is False


def test_size():
    game = Game(True, 8, False, True, 1)
    assert game.size == 8


def test_bot():
    game = Game(True, 8, False, True, 1)
    assert game.bot_active is False


def test_save():
    game = Game(True, 8, False, True, 1)
    assert game.get_save() == """pvp
8
Black
3 3
4 4

4 3
3 4
"""


def test_load():
    save = [
        'pve1',
        '8',
        'Black',
        '3 3',
        '4 4',
        '',
        '4 3',
        '3 4']
    game1 = Game(False, save)
    game2 = Game(True, 8, False, True, 1)
    assert len(game1.checkers) == len(game2.checkers)
