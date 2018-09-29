#!/usr/bin/env python3


from functools import partial
from PyQt5.QtGui import QIcon, QPainter, QFont, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QBasicTimer
from Game import Game
from Units import Checker
from Point import Point
from datetime import datetime
import os
from TurnThreads import TurnThread, BotThread, OnlineThread
import copy


class GameWindow(QMainWindow):
    EXIT_CODE_CHANGE_MODE = -123
    IMAGE_SIZE = 50
    SHIFT = 1
    BOT_SPEED = 1
    FONT = QFont("times", 20)
    TIMER_INTERVAL = 100

    def __init__(self, *args):
        super().__init__()

        self.ICON = QIcon('images/Icon.png')

        if len(args) < 4:
            raise ValueError
        is_new_game = args[0]
        if is_new_game:
            if len(args) != 7:
                raise ValueError
            self.__game = Game(args[0], args[1], args[2], args[3], args[4])
            self.is_online = args[5]
            self.socket = args[6]
        else:
            self.__game = Game(args[0], args[1])
            self.is_online = args[2]
            self.socket = args[3]

        self.me_first = args[3]
        self.is_game_over = False
        self.connection_lost = False
        self.__turn_thread = None
        self.end_game_timer = QBasicTimer()
        self.end_game_timer.start(self.TIMER_INTERVAL, self)

        self.WIDTH = (self.__game.size + self.SHIFT) * self.IMAGE_SIZE + self.IMAGE_SIZE * 12
        self.HEIGHT = (self.__game.size + self.SHIFT * 2) * self.IMAGE_SIZE + 20

        self.__log_name = None
        self.start_logging()

        self.checkers = copy.deepcopy(self.__game.checkers)
        self.turn = self.__game.is_white_turn
        self.score = copy.deepcopy(self.__game.score)

        self.initUI()
        self.show()

        if self.__game.PLAYER_IS_WHITE and self.__game.bot_active and not self.__game.is_white_turn:
            self.bot_thread = BotThread(self, self.BOT_SPEED, self.__game)
            self.bot_thread.start()
        elif self.is_online and not self.me_first:
            self.online_thread = OnlineThread(self.__game, self, None, True)
            self.online_thread.start()
        else:
            self.highlight_buttons()

    def initUI(self):
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint)
        self.set_geometry()
        self.setWindowIcon(self.ICON)
        self.setWindowTitle('Reversi')
        self.setStyleSheet('background: LightBlue;')

        self.__controls = []

        self.__checker_buttons = self.get_checker_buttons()

        self.__pass_button = self.create_button('Pass',
                                                (self.__game.size + self.SHIFT) * self.IMAGE_SIZE + 10,
                                                (self.SHIFT + self.__game.size - 1) * self.IMAGE_SIZE - 25,
                                                lambda: self.make_turn(self.__pass_button))

        self.__save_button = self.create_button('Save', self.WIDTH - self.IMAGE_SIZE * 7 - 20, 10, self.save)

        self.__settings_button = self.create_button('Settings', self.WIDTH - self.IMAGE_SIZE * 5 - 20, 10,
                                                    self.settings)

        self.__restart_button = self.create_button('Restart', self.WIDTH - self.IMAGE_SIZE * 3 - 10, 10,
                                                   partial(self.restart, True))

        self.__quit_button = self.create_button('Quit', self.WIDTH - self.IMAGE_SIZE - 20, 10, partial(self.quit, True))

    def copy_game_items(self):
        self.checkers = copy.deepcopy(self.__game.checkers)
        self.turn = self.__game.is_white_turn
        self.score = copy.deepcopy(self.__game.score)

    def start_logging(self):
        if not os.path.exists('logs') or not os.path.isdir('logs'):
            os.mkdir('logs')
        logs = os.listdir('logs')
        if len(logs) == 100:
            os.remove('logs/' + logs[0])
        self.__log_name = 'logs/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        game_info = 'Player VS '
        difficulty = Game.BOT_DIFFICULTIES[self.__game.BOT_DIFFICULTY]
        game_info += f'{difficulty} Bot' if self.__game.bot_active else 'Player'
        game_info += ' (Board size: {0}x{0})'.format(self.__game.size)
        self.log(game_info)

    def get_checker_buttons(self):
        buttons = {}
        for cell in self.__game.game_map:
            if cell.coordinates not in self.__game.occupied_coordinates:
                button = QPushButton('', self)
                coordinates = cell.coordinates.to_image_coordinates(self.IMAGE_SIZE, self.SHIFT)
                button.setGeometry(coordinates.x, coordinates.y, self.IMAGE_SIZE, self.IMAGE_SIZE)
                button.clicked.connect(partial(self.make_turn, button))
                button.setStyleSheet("background: transparent;")
                button.hide()
                buttons[cell.coordinates.to_tuple()] = button
        return buttons

    def create_button(self, name, x, y, action):
        button = QPushButton(name, self)
        button.setGeometry(x, y, self.IMAGE_SIZE, self.IMAGE_SIZE)
        button.clicked.connect(action)
        button.setStyleSheet("background: transparent; color: transparent;")
        self.__controls.append(button)
        return button

    def set_geometry(self):
        self.resize(self.WIDTH, self.HEIGHT)
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        self.move(self.x(), self.y() - 15)

    def save(self):
        folder = 'online' if self.is_online else 'offline'
        name = QFileDialog.getSaveFileName(self, 'Save', f'saves/{folder}', 'Save Files (*.save)')[0]
        if name == '':
            return False
        full_name = name if len(name) > 3 and name[-5:] == '.save' else name + '.save'
        with open(full_name, 'w') as file:
            text = self.__game.get_save()
            file.write(text)
        return True

    def ask_for_save(self):
        message = QMessageBox()
        message.move(self.x() + (self.width() - message.width()) / 2, self.y() + (self.height() - message.height()) / 2)
        choice = message.question(message, 'Save game?',
                                  'This will finish current game\nWould you like to save yor game?',
                                  QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        success = choice != QMessageBox.Cancel
        if choice == QMessageBox.Yes:
            success = self.save()
        return success

    def highlight_buttons(self):
        for cell in self.__game.game_map:
            if self.__game.check_turn(cell.coordinates) and cell.coordinates not in self.__game.occupied_coordinates:
                cell.highlight()
                button = self.get_button(cell.coordinates)
                if button is not None:
                    button.show()
        self.update()

    def hide_buttons(self):
        for cell in self.__game.game_map:
            cell.normalize()
            button = self.get_button(cell.coordinates)
            if button is not None and not button.isHidden():
                button.hide()
        self.update()

    def log(self, info):
        if self.__log_name is None:
            return
        with open(self.__log_name, 'a') as log_file:
            log_file.write(f'{datetime.now().strftime("%X")} {info}\n')

    def settings(self):
        if not self.ask_for_save():
            return
        qApp.exit(GameWindow.EXIT_CODE_CHANGE_MODE)

    def restart(self, to_ask):
        if to_ask and not self.ask_for_save():
            return
        bot_active = self.__game.bot_active
        size = self.__game.size
        player_first = self.__game.BOT_IS_WHITE
        bot_difficulty = self.__game.BOT_DIFFICULTY
        is_online = self.is_online
        socket = self.socket
        self.close()
        self.destroy()
        GameWindow(True, size, bot_active, player_first, bot_difficulty, is_online, socket)

    def quit(self, to_ask):
        if to_ask and not self.ask_for_save():
            return
        qApp.exit()

    def timerEvent(self, event):
        if self.is_game_over or self.connection_lost:
            self.game_over()

    def game_over(self):
        self.end_game_timer.stop()
        white_won = self.__game.score[Game.WHITE] > self.__game.score[Game.BLACK]
        log_color = Game.WHITE if white_won else Game.BLACK
        if self.__game.bot_active:
            player, bot = self.get_player_bot_colors()
            player_won = self.__game.score[player] > self.__game.score[bot]
            winner = Game.YOU if player_won else Game.BOT
            log_winner = Game.PLAYER if player_won else Game.BOT
        else:
            winner = log_color
            log_winner = Game.PLAYER
        is_draw = self.__game.score[Game.WHITE] == self.__game.score[Game.BLACK]
        if self.connection_lost:
            message = 'connection lost'
            self.log(message)
        else:
            message = 'Draw!' if is_draw else '{} won!'.format(winner)
            self.log('Draw' if is_draw else f'{log_winner} ({log_color}) won')
        self.create_game_over_window(message)

    def create_game_over_window(self, message):
        game_over_window = QMessageBox()
        game_over_window.setFont(QFont("times", 12))
        game_over_window.setWindowIcon(self.ICON)
        game_over_window.setWindowTitle('Game Over')
        game_over_window.setText(message)
        restart = game_over_window.addButton('Restart', QMessageBox.AcceptRole)
        if self.connection_lost:
            restart.setEnabled(False)
        game_over_window.addButton('Quit', QMessageBox.RejectRole)
        game_over_window.exec()
        if game_over_window.clickedButton() == restart:
            self.restart(False)
        else:
            self.quit(False)

    def make_turn(self, button):
        self.update()
        if not self.is_online:
            self.offline_turn(button)
        else:
            self.online_turn(button)
        if self.is_game_over or self.connection_lost:
            self.game_over()

    def offline_turn(self, button):
        self.__turn_thread = TurnThread(self, self.IMAGE_SIZE, self.SHIFT, self.BOT_SPEED, self.__game,
                                        self.__pass_button, button)
        self.__turn_thread.start()

    def online_turn(self, button):
        if button == self.__pass_button:
            coordinates = None
        else:
            coordinates = Point(button.x(), button.y()).to_cell_coordinates(self.IMAGE_SIZE,
                                                                            self.SHIFT)
        self.__turn_thread = OnlineThread(self.__game, self, coordinates)
        self.__turn_thread.start()

    def remove_button(self, coordinates):
        coordinates = coordinates.to_tuple()
        self.__checker_buttons[coordinates].hide()
        self.__checker_buttons.pop(coordinates)

    def get_button(self, coordinates):
        coordinates = coordinates.to_tuple()
        if coordinates not in self.__checker_buttons:
            return None
        return self.__checker_buttons[coordinates]

    def get_player_bot_colors(self):
        if self.__game.PLAYER_IS_WHITE:
            player = Game.WHITE
            bot = Game.BLACK
        else:
            player = Game.BLACK
            bot = Game.WHITE
        return player, bot

    def paintEvent(self, event):
        # if not self.__game.bot_active or self.__turn_thread is not None and self.__turn_thread.bot_turn_finished:
        #     self.copy_game_items()

        painter = QPainter()
        painter.begin(self)

        self.draw_cells(painter)
        self.draw_signature(painter)
        self.draw_controls(painter)
        self.draw_checkers(painter)
        self.draw_turn(painter)
        self.draw_score(painter)
        if self.__game.bot_active:
            self.draw_bot(painter)

        painter.end()

    def draw_controls(self, painter):
        painter.setFont(self.FONT)
        for button in self.__controls:
            painter.drawImage(button.x(), button.y(),
                              QImage(f'images/{button.text()}.png').scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))
            painter.drawText(button.x() - self.IMAGE_SIZE / 2,
                             button.y(), self.IMAGE_SIZE * 2, self.IMAGE_SIZE + 30,
                             Qt.AlignCenter | Qt.AlignBottom, button.text())

    def draw_bot(self, painter):
        painter.setFont(self.FONT)
        difficulty = self.__game.BOT_DIFFICULTIES[self.__game.BOT_DIFFICULTY]
        painter.drawText((self.SHIFT + 1) * self.IMAGE_SIZE + 10, self.HEIGHT - 10,
                         f'Bot difficulty: {difficulty}')
        painter.drawImage(self.SHIFT * self.IMAGE_SIZE, self.HEIGHT - self.IMAGE_SIZE - 10,
                          QImage(f'images/{difficulty}.png').scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))

    def draw_signature(self, painter):
        painter.drawText(self.WIDTH - 125, self.HEIGHT - 10, 'Made by Artemiy Izakov')

    def draw_score(self, painter):
        painter.setFont(self.FONT)
        x = (self.__game.size + self.SHIFT) * self.IMAGE_SIZE + 10
        y = self.SHIFT * self.IMAGE_SIZE + 20
        painter.drawText(x, y, 'Score:')
        shift = self.IMAGE_SIZE
        y += 3
        painter.drawImage(x, y,
                          Checker.WHITE.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))
        painter.drawImage(x, y + shift,
                          Checker.BLACK.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))
        if not self.__game.bot_active:
            for color, score in self.score.items():
                painter.drawText(x + self.IMAGE_SIZE, y + shift - 15, '{}: {}'.format(color, score))
                shift *= 2
        else:
            player, bot = self.get_player_bot_colors()
            if self.__game.PLAYER_IS_WHITE:
                painter.drawText(x + self.IMAGE_SIZE, y + shift - 15, f'{Game.YOU}: {self.score[player]}')
                painter.drawText(x + self.IMAGE_SIZE, y + shift * 2 - 15, f'{Game.BOT}: {self.score[bot]}')
            else:
                painter.drawText(x + self.IMAGE_SIZE, y + shift - 15, f'{Game.BOT}: {self.score[bot]}')
                painter.drawText(x + self.IMAGE_SIZE, y + shift * 2 - 15, f'{Game.YOU}: {self.score[player]}')

    def draw_turn(self, painter):
        painter.setFont(self.FONT)
        if not self.__game.bot_active:
            turn = 'First Player' if not self.turn else 'Second Player'
            text = fr"{turn}'s turn"
        else:
            turn = Game.YOU + "r" if self.turn == self.__game.PLAYER_IS_WHITE else Game.BOT + "'s"
            text = fr"{turn} turn"
        painter.drawText((self.SHIFT + 1) * self.IMAGE_SIZE, 35, text)
        image = Checker.WHITE if self.turn else Checker.BLACK
        painter.drawImage(self.SHIFT * self.IMAGE_SIZE, 0, image.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))

    def draw_cells(self, painter):
        for cell in self.__game.game_map:
            self.draw(cell.image, cell.coordinates, painter)

    def draw_checkers(self, painter):
        for checker in self.checkers:
            self.draw(checker.image, checker.coordinates, painter)

    def draw(self, image, coordinates, painter):
        image_coordinates = coordinates.to_image_coordinates(self.IMAGE_SIZE, 1)
        x = image_coordinates.x
        y = image_coordinates.y
        painter.drawImage(x, y, image.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))
