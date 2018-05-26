#!/usr/bin/env python3


from functools import partial
from PyQt5.QtGui import QIcon, QPainter, QFont, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread
from Point import Point
from Game import Game
from Units import Checker
from datetime import datetime
import time
import os


class TurnThread(QThread):

    def __init__(self, game_window, game, pass_button, button):
        super().__init__()
        self.daemon = True
        self.__game_window = game_window
        self.__game = game
        self.__button = button
        self.__pass_button = pass_button

    def player_turn(self):
        coordinates = Point(self.__button.x(), self.__button.y()).to_cell_coordinates(GameWindow.IMAGE_SIZE,
                                                                                      GameWindow.SHIFT)
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
        time.sleep(GameWindow.BOT_SPEED)
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


class GameWindow(QMainWindow):

    EXIT_CODE_CHANGE_MODE = -123
    IMAGE_SIZE = 50
    SHIFT = 1
    BOT_SPEED = 1
    FONT = QFont("times", 20)

    def __init__(self, *args):
        super().__init__()

        self.ICON = QIcon('images/Icon.png')

        self.is_game_over = False

        if len(args) < 2:
            raise ValueError
        is_new_game = args[0]
        if is_new_game:
            if len(args) != 5:
                raise ValueError
        if is_new_game:
            self.__game = Game(args[0], args[1], args[2], args[3], args[4])
        else:
            self.__game = Game(args[0], args[1])
        self.last_player_turn_result = True

        self.__width = (self.__game.size + self.SHIFT) * self.IMAGE_SIZE + self.IMAGE_SIZE * 12
        self.__height = (self.__game.size + self.SHIFT * 2) * self.IMAGE_SIZE + 20

        logs = os.listdir('logs')
        if len(logs) == 100:
            os.remove('logs/' + logs[0])
        self.__log_name = 'logs/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        game_info = 'Player VS '
        difficulty = Game.BOT_DIFFICULTIES[self.__game.BOT_DIFFICULTY]
        game_info += f'{difficulty} Bot' if self.__game.bot_active else 'Player'
        game_info += ' (Board size: {0}x{0})'.format(self.__game.size)
        self.log(game_info)

        self.initUI()
        self.show()

        if self.__game.PLAYER_IS_WHITE and self.__game.bot_active and not self.__game.is_white_turn:
            self.bot_turn()
        self.highlight_buttons()

    def initUI(self):
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint)
        self.set_geometry()
        self.setWindowIcon(self.ICON)
        self.setWindowTitle('Reversi')
        self.setStyleSheet('background: LightBlue;')
        # self.setStyleSheet('background-image: url("images/wood.png");')

        self.__controls = []

        self.__checker_buttons = self.get_checker_buttons()

        self.__pass_button = self.create_button('Pass',
                                                (self.__game.size + self.SHIFT) * self.IMAGE_SIZE + 10,
                                                (self.SHIFT + self.__game.size - 1) * self.IMAGE_SIZE - 25,
                                                lambda: self.make_turn(self.__pass_button))

        self.__save_button = self.create_button('Save', self.__width - self.IMAGE_SIZE * 7 - 20, 10, self.save)

        self.__settings_button = self.create_button('Settings', self.__width - self.IMAGE_SIZE * 5 - 20, 10, self.settings)

        self.__restart_button = self.create_button('Restart', self.__width - self.IMAGE_SIZE * 3 - 10, 10, partial(self.restart, True))

        self.__quit_button = self.create_button('Quit', self.__width - self.IMAGE_SIZE - 20, 10, partial(self.quit, True))

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
        self.resize(self.__width, self.__height)
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        self.move(self.x(), self.y() - 15)

    def save(self):
        name = QFileDialog.getSaveFileName(self, 'Save', 'saves/', 'Reversy Save (*.rs)')[0]
        if name == '':
            return False
        full_name = name if len(name) > 3 and name[-3:] == '.rs' else name + '.rs'
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
        self.close()
        self.destroy()
        GameWindow(True, size, bot_active, player_first, bot_difficulty)

    def quit(self, to_ask):
        if to_ask and not self.ask_for_save():
            return
        qApp.exit()

    def game_over(self):
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
        game_over_window.addButton('Quit', QMessageBox.RejectRole)
        game_over_window.exec()
        if game_over_window.clickedButton() == restart:
            self.restart(False)
        else:
            self.quit(False)

    def make_turn(self, button):
        self.update()
        thread = TurnThread(self, self.__game, self.__pass_button, button)
        thread.start()
        if self.is_game_over:
            self.game_over()
        # player_turn = self.player_turn(button)
        # self.hide_buttons()
        # if self.__game.is_finished:
        #     self.game_over()
        #     return
        # bot_turn = True
        # if self.__game.bot_active:
        #     # thread = Thread(target=self.bot_turn)
        #     # thread.start()
        #     # thread.join()
        #     # bot_turn = True
        #     bot_turn = self.bot_turn()
        # if self.__game.is_finished or (not player_turn and not bot_turn) or \
        #         (not self.__game.bot_active and not player_turn and not self.__last_player_turn_result):
        #     self.game_over()
        #     return
        # self.__last_player_turn_result = player_turn
        # # self.highlight_buttons()
        # self.update()

    def bot_turn(self):
        self.repaint()
        # thread = BotThread(self, self.__game)
        # thread.start()
        # thread.join()
        time.sleep(self.BOT_SPEED)
        bot_checker_coordinates = self.__game.bot_turn()
        success = bot_checker_coordinates is not None
        if success:
            self.remove_button(bot_checker_coordinates)
            log_message = f'placed checker at {bot_checker_coordinates}'
        else:
            log_message = 'passed'
        bot_color = Game.WHITE if self.__game.BOT_IS_WHITE else Game.BLACK
        self.log(f"Bot's turn\t({bot_color}): {log_message}")
        return success

    def player_turn(self, button):
        coordinates = Point(button.x(), button.y()).to_cell_coordinates(self.IMAGE_SIZE, self.SHIFT)
        color = Game.WHITE if self.__game.is_white_turn else Game.BLACK
        if button == self.__pass_button:
            self.log(f"Player's turn\t({color}): passed")
            self.__game.pass_turn()
            return False
        self.log(f"Player's turn\t({color}): placed checker at {coordinates}")
        self.__game.make_turn(coordinates)
        self.remove_button(coordinates)
        return True

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
        painter = QPainter()
        painter.begin(self)

        self.draw_cells(painter)
        self.draw_checkers(painter)
        self.draw_signature(painter)
        self.draw_turn(painter)
        self.draw_score(painter)
        self.draw_controls(painter)

        if self.__game.bot_active:
            self.draw_bot(painter)

        painter.end()

    def draw_controls(self, painter):
        for button in self.__controls:
            painter.drawImage(button.x(), button.y(),
                              QImage(f'images/{button.text()}.png').scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))
            painter.drawText(button.x() - self.IMAGE_SIZE / 2,
                             button.y(), self.IMAGE_SIZE * 2, self.IMAGE_SIZE + 30,
                             Qt.AlignCenter | Qt.AlignBottom, button.text())

    def draw_bot(self, painter):
        painter.setFont(self.FONT)
        difficulty = self.__game.BOT_DIFFICULTIES[self.__game.BOT_DIFFICULTY]
        painter.drawText((self.SHIFT + 1) * self.IMAGE_SIZE + 10, self.__height - 10,
                         f'Bot difficulty: {difficulty}')
        painter.drawImage(self.SHIFT * self.IMAGE_SIZE, self.__height - self.IMAGE_SIZE - 10,
                          QImage(f'images/{difficulty}.png').scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))

    def draw_signature(self, painter):
        painter.drawText(self.__width - 125, self.__height - 10, 'Made by Artemiy Izakov')

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
            for color, score in self.__game.score.items():
                painter.drawText(x + self.IMAGE_SIZE, y + shift - 15, '{}: {}'.format(color, score))
                shift *= 2
        else:
            player, bot = self.get_player_bot_colors()
            if self.__game.PLAYER_IS_WHITE:
                painter.drawText(x + self.IMAGE_SIZE, y + shift - 15, f'{Game.YOU}: {self.__game.score[player]}')
                painter.drawText(x + self.IMAGE_SIZE, y + shift * 2 - 15, f'{Game.BOT}: {self.__game.score[bot]}')
            else:
                painter.drawText(x + self.IMAGE_SIZE, y + shift - 15, f'{Game.BOT}: {self.__game.score[bot]}')
                painter.drawText(x + self.IMAGE_SIZE, y + shift * 2 - 15, f'{Game.YOU}: {self.__game.score[player]}')

    def draw_turn(self, painter):
        painter.setFont(self.FONT)
        if not self.__game.bot_active:
            turn = 'First Player' if not self.__game.is_white_turn else 'Second Player'
            text = fr"{turn}'s turn"
        else:
            turn = Game.YOU + "r" if self.__game.is_white_turn == self.__game.PLAYER_IS_WHITE else Game.BOT + "'s"
            text = fr"{turn} turn"
        painter.drawText((self.SHIFT + 1) * self.IMAGE_SIZE, 35, text)
        image = Checker.WHITE if self.__game.is_white_turn else Checker.BLACK
        painter.drawImage(self.SHIFT * self.IMAGE_SIZE, 0, image.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))

    def draw_cells(self, painter):
        for cell in self.__game.game_map:
            self.draw(cell.image, cell.coordinates, painter)

    def draw_checkers(self, painter):
        for checker in self.__game.checkers:
            self.draw(checker.image, checker.coordinates, painter)

    def draw(self, image, coordinates, painter):
        image_coordinates = coordinates.to_image_coordinates(self.IMAGE_SIZE, 1)
        x = image_coordinates.x
        y = image_coordinates.y
        painter.drawImage(x, y, image.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))
