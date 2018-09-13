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
            return
        self.__game_window.log(f"Player's turn\t({color}): placed checker at {coordinates}")
        self.__game.make_turn(coordinates)
        self.__game_window.remove_button(coordinates)

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

    def run(self):
        self.player_turn()
        self.__game_window.hide_buttons()
        if self.__game.is_finished:
            self.__game_window.is_game_over = True
            return
        if self.__game.bot_active:
            self.bot_turn()
        if self.__game.is_finished:
            self.__game_window.is_game_over = True
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


class OnlineThread(QThread):

    def __init__(self, game, game_window, coordinates, just_waiting=False):
        super().__init__()
        self.daemon = True
        self.game = game
        self.game_window = game_window
        self.coordinates = coordinates
        self.just_waiting = just_waiting

    def check_game(self):
        if self.game.is_finished:
            self.game_window.is_game_over = True
            return True

    def run(self):
        if not self.just_waiting:
            self.game_window.socket.make_turn(self.game, self.game_window, self.coordinates)
        if self.check_game() or self.game_window.connection_lost:
            return
        self.game_window.update()
        self.game_window.socket.wait_for_turn(self.game, self.game_window)
        if self.check_game() or self.game_window.connection_lost:
            return

