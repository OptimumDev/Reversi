#!/usr/bin/env python3


from PyQt5.QtCore import QThread
from Point import Point
from Game import Game
import time


class TurnThread(QThread):

    def __init__(self, game_window, image_size, shift, bot_speed, game, pass_button, button):
        super().__init__()
        self.daemon = True
        self.__game_window = game_window
        self.__game = game
        self.__button = button
        self.__pass_button = pass_button
        self.__image_size = image_size
        self.__shift = shift
        self.__bot_speed = bot_speed

    def player_turn(self):
        coordinates = Point(self.__button.x(), self.__button.y()).to_cell_coordinates(self.__image_size,
                                                                                      self.__shift)
        color = Game.WHITE if self.__game.is_white_turn else Game.BLACK
        if self.__button == self.__pass_button:
            self.__game_window.log(f"Player's turn\t({color}): passed")
            self.__game.pass_turn()
            return False
        self.__game_window.log(f"Player's turn\t({color}): placed checker at {coordinates}")
        self.__game.make_turn(coordinates)
        self.__game_window.remove_button(coordinates)
        return True

    def bot_turn(self):
        time.sleep(self.__bot_speed)
        bot_checker_coordinates = self.__game.bot_turn()
        success = bot_checker_coordinates is not None
        if success:
            self.__game_window.remove_button(bot_checker_coordinates)
            log_message = f'placed checker at {bot_checker_coordinates}'
        else:
            log_message = 'passed'
        bot_color = Game.WHITE if self.__game.BOT_IS_WHITE else Game.BLACK
        self.__game_window.log(f"Bot's turn\t({bot_color}): {log_message}")
        return success

    def run(self):
        player_turn = self.player_turn()
        self.__game_window.hide_buttons()
        if self.__game.is_finished:
            self.__game_window.is_game_over = True
            return
        bot_turn = True
        if self.__game.bot_active:
            bot_turn = self.bot_turn()
        if self.__game.is_finished or (not player_turn and not bot_turn) or \
                (not self.__game.bot_active and not player_turn and not self.__game_window.last_player_turn_result):
            self.__game_window.is_game_over = True
            return
        self.__game_window.last_player_turn_result = player_turn
        self.__game_window.highlight_buttons()
        self.__game_window.update()


class BotThread(QThread):

    def __init__(self, game_window, bot_speed, game):
        super().__init__()
        self.daemon = True
        self.__game_window = game_window
        self.__game = game
        self.__bot_speed = bot_speed

    def run(self):
        time.sleep(self.__bot_speed)
        bot_checker_coordinates = self.__game.bot_turn()
        success = bot_checker_coordinates is not None
        if success:
            self.__game_window.remove_button(bot_checker_coordinates)
            log_message = f'placed checker at {bot_checker_coordinates}'
        else:
            log_message = 'passed'
        bot_color = Game.WHITE if self.__game.BOT_IS_WHITE else Game.BLACK
        self.__game_window.log(f"Bot's turn\t({bot_color}): {log_message}")
        self.__game_window.highlight_buttons()
