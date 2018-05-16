#!/usr/bin/env python3


from functools import partial
from PyQt5.QtGui import QIcon, QPainter, QFont, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from Point import Point
from Game import Game
from Units import Checker
from datetime import datetime
import time
import os


class ChooseModeWindow(QWidget):
    BUTTON_WIDTH = 250
    BUTTON_HEIGHT = 50
    MODE_SHIFT = 100
    UPPER_SHIFT = 100
    SIDE_SHIFT = 50

    def __init__(self):
        super().__init__()

        self.__width = (self.BUTTON_WIDTH + self.SIDE_SHIFT * 2) * 2 + self.MODE_SHIFT
        self.__height = self.BUTTON_HEIGHT * 2 + self.UPPER_SHIFT * 2
        self.__font = QFont("times", 20)
        self.__box_font = QFont("times", 15)

        self.__board_size = 8
        self.__player_first = True
        self.__bot_difficulty = 1

        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)
        self.resize(self.__width, self.__height)
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        self.setWindowTitle('Game Settings')
        self.setWindowIcon(QIcon('images/icon.png'))

        self.__board_size_box = QComboBox(self)
        self.__board_size_box.setFont(self.__box_font)
        self.__board_size_box.addItems([str(i) for i in range(4, 19, 2)])
        self.__board_size_box.setCurrentIndex(2)
        self.__board_size_box.move(self.__width // 2 + 50, self.UPPER_SHIFT - 40)
        self.__board_size_box.activated[str].connect(self.board_size_choice)

        self.__pvp_button = QPushButton('Player VS Player', self)
        self.__pvp_button.setFont(self.__font)
        self.__pvp_button.setGeometry(self.SIDE_SHIFT + self.MODE_SHIFT, self.UPPER_SHIFT,
                                      self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        self.__pvp_button.clicked.connect(partial(self.run, False))

        self.__pve_button = QPushButton('Player VS Bot', self)
        self.__pve_button.setFont(self.__font)
        self.__pve_button.setGeometry(self.SIDE_SHIFT * 2 + self.BUTTON_WIDTH + self.MODE_SHIFT,
                                      self.UPPER_SHIFT, self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        self.__pve_button.clicked.connect(partial(self.run, True))

        self.__player_first_checkbox = QCheckBox("Player go first", self)
        self.__player_first_checkbox.setFont(self.__font)
        self.__player_first_checkbox.toggle()
        self.__player_first_checkbox.move(30 + self.__pve_button.x(), self.__pve_button.y() + self.BUTTON_HEIGHT)
        self.__player_first_checkbox.stateChanged.connect(self.player_first_change)

        self.__bot_difficulty_box = QComboBox(self)
        self.__bot_difficulty_box.setFont(self.__box_font)
        self.__bot_difficulty_box.addItems(['Easy', 'Normal', 'Hard'])
        self.__bot_difficulty_box.setCurrentIndex(1)
        self.__bot_difficulty_box.setGeometry(165 + self.__pve_button.x(),
                                              self.__pve_button.y() + self.BUTTON_HEIGHT + 35, 100, 30)
        self.__bot_difficulty_box.activated[int].connect(self.bot_difficulty_choice)

        self.__load_button = QPushButton('Load', self)
        self.__load_button.setFont(self.__font)
        self.__load_button.setGeometry((self.__width - self.BUTTON_WIDTH) // 2,
                                       self.UPPER_SHIFT * 2 + self.BUTTON_HEIGHT - 10,
                                       self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
        self.__load_button.clicked.connect(self.load)

    def bot_difficulty_choice(self, difficulty):
        self.__bot_difficulty = difficulty

    def board_size_choice(self, size):
        self.__board_size = int(size)

    def player_first_change(self):
        self.__player_first = not self.__player_first

    def load(self):
        name = QFileDialog.getOpenFileName(self, 'Chose Save File', 'saves/', 'Reversy Save (*.rs)')[0]
        if name == '':
            return
        GameWindow(False, name)
        self.hide()

    def run(self, bot_active):
        GameWindow(True, self.__board_size, bot_active, self.__player_first, self.__bot_difficulty)
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.setFont(self.__font)

        painter.drawText(self.__width // 2 - 85, 30, 'Game Settings')
        painter.drawText(self.__width // 2 - 95, self.UPPER_SHIFT - 15, 'Board Size:')
        painter.drawText(10, self.UPPER_SHIFT + 35, 'New Game:')
        painter.drawText(self.__pvp_button.x() + self.BUTTON_WIDTH + 10, self.UPPER_SHIFT + 35, 'Or')
        painter.drawText(self.__pve_button.x() - 5, self.__pve_button.y() + self.BUTTON_HEIGHT + 60, 'Bot Difficulty:')

        painter.end()


class GameWindow(QMainWindow):

    EXIT_CODE_CHANGE_MODE = -123
    IMAGE_SIZE = 50

    def __init__(self, *args):
        super().__init__()
        if len(args) < 2:
            raise ValueError
        is_new_game = args[0]
        if is_new_game:
            if len(args) != 5:
                raise ValueError
        self.__shift = 1
        self.__bot_speed = 1
        self.__font = QFont("times", 20)
        if is_new_game:
            self.__game = Game(args[0], args[1], args[2], args[3], args[4])
        else:
            self.__game = Game(args[0], args[1])
        self.__last_player_turn_result = 0

        self.__width = (self.__game.size + self.__shift) * self.IMAGE_SIZE + 600
        self.__height = (self.__game.size + self.__shift * 2) * self.IMAGE_SIZE + 20

        logs = os.listdir('logs')
        if len(logs) == 100:
            os.remove('logs/' + logs[0])
        self.__log_name = 'logs/' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
        game_info = 'Player VS '
        difficulty = Game.BOT_DIFFICULTIES[self.__game.BOT_DIFFICULTY]
        game_info += '{} Bot'.format(difficulty) if self.__game.bot_active else 'Player'
        game_info += ' (Board size: {0}x{0})'.format(self.__game.size)
        self.log(game_info)

        self.initUI()
        self.show()

        if self.__game.PLAYER_IS_WHITE and self.__game.bot_active and not self.__game.is_white_turn:
            self.bot_turn()
        self.highlight_buttons()

    def initUI(self):
        self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint | Qt.WindowTitleHint)

        self.resize(self.__width, self.__height)
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())
        self.move(self.x(), self.y() - 15)

        self.setWindowIcon(QIcon('images/icon.png'))
        self.setWindowTitle('Reversi')

        self.__controls = []

        self.__checker_buttons = self.get_checker_buttons()

        self.__pass_button = self.create_button('Pass',
                                                (self.__game.size + self.__shift) * self.IMAGE_SIZE + 10,
                                                (self.__shift + 2) * self.IMAGE_SIZE,
                                                lambda: self.make_turn(self.__pass_button))

        self.__save_button = self.create_button('Save', self.__width - 370, 10, self.save)

        self.__chose_mode_button = self.create_button('Settings', self.__width - 270, 10, self.chose_mod)

        self.__restart_button = self.create_button('Restart', self.__width - 160, 10, lambda: self.restart(True))

        self.__quit_button = self.create_button('Quit', self.__width - 70, 10, lambda: self.quit(True))

    def get_checker_buttons(self):
        buttons = []
        for cell in self.__game.game_map:
            if cell.coordinates not in self.__game.occupied_coordinates:
                button = QPushButton('', self)
                coordinates = cell.coordinates.to_image_coordinates(self.IMAGE_SIZE, self.__shift)
                button.setGeometry(coordinates.x, coordinates.y, self.IMAGE_SIZE, self.IMAGE_SIZE)
                button.clicked.connect(partial(self.make_turn, button))
                button.setStyleSheet("background: transparent")
                buttons.append(button)
        return buttons

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
        choice = QMessageBox.question(self, 'Save game?',
                                      'This will finish current game\nWould you like to save yor game?',
                                      QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
        success = choice != QMessageBox.Cancel
        if choice == QMessageBox.Yes:
            success = self.save()
        return success

    def create_button(self, name, x, y, action):
        button = QPushButton(name, self)
        button.setGeometry(x, y, self.IMAGE_SIZE, self.IMAGE_SIZE)
        button.clicked.connect(action)
        button.setStyleSheet("background: transparent; color: transparent;")
        self.__controls.append(button)
        return button

    def highlight_buttons(self):
        for cell in self.__game.game_map:
            if self.__game.check_turn(cell.coordinates) and cell.coordinates not in self.__game.occupied_coordinates:
                cell.highlight()
        self.update()

    def hide_buttons(self):
        for cell in self.__game.game_map:
            cell.normalize()
        self.update()

    def log(self, info):
        with open(self.__log_name, 'a') as log_file:
            log_file.write('{} {}\n'.format(datetime.now().strftime('%X'), info))

    def settings(self):
        pass

    def chose_mod(self):
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
        self.log('Draw' if is_draw else '{} ({}) won'.format(log_winner, log_color))
        game_over_window = QMessageBox()
        game_over_window.setFont(QFont("times", 12))
        game_over_window.setWindowIcon(QIcon('images/icon.png'))
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
        player_turn = self.player_turn(button)
        if player_turn == 2:
            return
        self.hide_buttons()
        if self.__game.is_finished:
            self.game_over()
            return
        bot_turn = True
        if self.__game.bot_active:
            bot_turn = self.bot_turn()
        if self.__game.is_finished or (player_turn == 1 and not bot_turn) or \
                (not self.__game.bot_active and player_turn == 1 and self.__last_player_turn_result == 1):
            self.game_over()
            return
        self.__last_player_turn_result = player_turn
        self.highlight_buttons()
        self.update()

    def bot_turn(self):
        self.repaint()
        time.sleep(self.__bot_speed)
        bot_checker_coordinates = self.__game.bot_turn()
        success = bot_checker_coordinates is not None
        if success:
            checker_button = self.get_button(bot_checker_coordinates)
            self.remove_button(checker_button)
            log_message = 'placed checker at {}'.format(bot_checker_coordinates)
        else:
            log_message = 'passed'
        bot_color = Game.WHITE if self.__game.BOT_IS_WHITE else Game.BLACK
        self.log("Bot's turn\t({}): {}".format(bot_color, log_message))
        return success

    def player_turn(self, button):
        coordinates = Point(button.x(), button.y()).to_cell_coordinates(self.IMAGE_SIZE, self.__shift)
        color = Game.WHITE if self.__game.is_white_turn else Game.BLACK
        if button == self.__pass_button:
            self.log("Player's turn\t({}): passed".format(color))
            self.__game.pass_turn()
            return 1
        if not self.__game.check_turn(coordinates):
            return 2
        self.log("Player's turn\t({}): placed checker at {}".format(color, coordinates))
        self.__game.make_turn(coordinates)
        self.remove_button(button)
        return 0

    def remove_button(self, button):
        button.hide()
        self.__checker_buttons.remove(button)

    def get_button(self, coordinates):
        for button in self.__checker_buttons:
            button_coordinates = Point(button.x(), button.y()).to_cell_coordinates(self.IMAGE_SIZE, self.__shift)
            if coordinates == button_coordinates:
                return button

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
        painter.setFont(self.__font)
        difficulty = self.__game.BOT_DIFFICULTIES[self.__game.BOT_DIFFICULTY]
        painter.drawText((self.__shift + 1) * self.IMAGE_SIZE + 10, self.__height - 10,
                         f'Bot difficulty: {difficulty}')
        painter.drawImage(self.__shift * self.IMAGE_SIZE, self.__height - self.IMAGE_SIZE - 10,
                          QImage(f'images/{difficulty}Bot.png').scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))

    def draw_signature(self, painter):
        painter.drawText(self.__width - 125, self.__height - 10, 'Made by Artemiy Izakov')

    def draw_score(self, painter):
        painter.setFont(self.__font)
        x = (self.__game.size + self.__shift) * self.IMAGE_SIZE + 10
        y = self.__shift * self.IMAGE_SIZE + 20
        painter.drawText(x, y, 'Score:')
        shift = 30
        if not self.__game.bot_active:
            for color, score in self.__game.score.items():
                painter.drawText(x, y + shift, '{}: {}'.format(color, score))
                shift *= 2
        else:
            player, bot = self.get_player_bot_colors()
            painter.drawText(x, y + shift, '{}: {}'.format(Game.YOU, self.__game.score[player]))
            painter.drawText(x, y + shift * 2, '{}: {}'.format(Game.BOT, self.__game.score[bot]))

    def draw_turn(self, painter):
        painter.setFont(self.__font)
        if not self.__game.bot_active:
            turn = 'First Player' if not self.__game.is_white_turn else 'Second Player'
            text = r"{}'s turn".format(turn)
        else:
            turn = Game.YOU + "r" if self.__game.is_white_turn == self.__game.PLAYER_IS_WHITE else Game.BOT + "'s"
            text = r"{} turn".format(turn)
        painter.drawText((self.__shift + 1) * self.IMAGE_SIZE, 35, text)
        image = Checker.WHITE if self.__game.is_white_turn else Checker.BLACK
        painter.drawImage(self.__shift * self.IMAGE_SIZE, 0, image.scaled(self.IMAGE_SIZE, self.IMAGE_SIZE))

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
