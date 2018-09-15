#!/usr/bin/env python3


from PyQt5.QtGui import QIcon, QPainter, QFont, QImage, QMovie, QPen, QColor
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QBasicTimer
from functools import partial
from GameWindow import GameWindow
from OnlineMode import Server, Client


class SettingsWindow(QWidget):
    BUTTON_SIZE = 100
    UPPER_SHIFT = 100
    SIDE_SHIFT = 50
    BETWEEN_SHIFT = 50
    WIDTH = BUTTON_SIZE * 4 + SIDE_SHIFT * 2 + BETWEEN_SHIFT * 3
    HEIGHT = BUTTON_SIZE * 2 + UPPER_SHIFT * 2 + BETWEEN_SHIFT
    TWO_BUTTONS_POSITIONS = (SIDE_SHIFT + BETWEEN_SHIFT + BUTTON_SIZE / 2,
                             WIDTH - SIDE_SHIFT - BETWEEN_SHIFT - BUTTON_SIZE * 3 / 2)
    ONE_LINE_UPPER_SHIFT = UPPER_SHIFT * 3 / 2

    def __init__(self):
        super().__init__()

        # font, ok = QFontDialog().getFont()

        self.__font = QFont('', 20)
        self.__board_size = 8
        self.__is_online = False
        self.__is_player_first = True
        self.__is_bot_active = False
        self.__bot_difficulty = 1
        self.__ip = ''
        self.socket = None
        self.ip_error = False

        self.__controls = []
        self.__current_title = 'Game Mode'

        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowFlag(Qt.MSWindowsFixedSizeDialogHint)
        self.resize(self.WIDTH, self.HEIGHT)
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        self.setWindowTitle('Game Settings')
        self.setWindowIcon(QIcon('images/icon.png'))
        self.setStyleSheet('background: LightBlue;')

        self.starting()

    def create_button(self, name, x, y, action, width=100, height=100):
        button = QPushButton(name, self)
        button.setGeometry(x, y, width, height)
        button.clicked.connect(action)
        button.setStyleSheet("background: transparent; color: transparent;")
        button.show()
        self.__controls.append(button)
        return button

    def create_back_button(self, action):
        return self.create_button('Back', self.WIDTH - self.BUTTON_SIZE - 5, self.HEIGHT - 60,
                                  action, self.BUTTON_SIZE, 30)

    def set_up(self):
        self.update()
        for button in self.__controls:
            button.hide()
        self.__controls = []

    def starting(self):
        self.set_up()
        self.__current_title = 'Choose Game Mode'
        offline = self.create_button("Offline", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, self.offline)
        online = self.create_button("Online", self.TWO_BUTTONS_POSITIONS[1], offline.y(), self.online)

    def offline(self):
        self.__is_online = False
        self.new_load()

    def online(self):
        self.__is_online = True
        self.host_join()

    def host_join(self):
        self.set_up()
        self.__current_title = 'Host or Join?'
        host = self.create_button("Host", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, self.choose_size)
        #                                                                                           self.new_load)
        join = self.create_button("Join", self.TWO_BUTTONS_POSITIONS[1], host.y(), self.ip)
        back = self.create_back_button(self.starting)

    def new_load(self):
        self.set_up()
        self.__current_title = 'New or Load?'
        new = self.create_button("New Game", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT,
                                 self.choose_size if self.__is_online else self.pvp_pve)
        load = self.create_button("Load", self.TWO_BUTTONS_POSITIONS[1], new.y(), self.load)
        back = self.create_back_button(self.host_join if self.__is_online else self.starting)

    def choose_size(self):
        self.set_up()
        self.__current_title = 'Choose Board Size'
        for i in range(4, 9, 2):
            button = self.create_button(f'{i}x{i}', self.BUTTON_SIZE / 2 + self.SIDE_SHIFT +
                                        (i - 4) / 2 * (self.BUTTON_SIZE + self.BETWEEN_SHIFT * 3 / 2),
                                        self.UPPER_SHIFT,
                                        partial(self.change_size, i))
        for i in range(10, 17, 2):
            button = self.create_button(f'{i}x{i}',
                                        self.SIDE_SHIFT + (i - 10) / 2 * (self.BUTTON_SIZE + self.BETWEEN_SHIFT),
                                        self.UPPER_SHIFT + self.BUTTON_SIZE + self.BETWEEN_SHIFT,
                                        partial(self.change_size, i))
        back = self.create_back_button(self.new_load if self.__is_online else
                                       (self.bot if self.__is_bot_active else self.pvp_pve))

    def change_size(self, size):
        self.__board_size = size
        if self.__is_online or self.__is_bot_active:
            self.first()
        else:
            self.run()

    def first(self):
        self.set_up()
        self.__current_title = 'Who Will Be The First'
        self.__controls = []
        me = self.create_button("Me", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT,
                                partial(self.make_first, True))
        other = self.create_button("Second Player" if self.__is_online else "Bot", self.TWO_BUTTONS_POSITIONS[1], me.y(),
                                   partial(self.make_first, False))
        back = self.create_back_button(self.choose_size)

    def make_first(self, me_first):
        self.__is_player_first = me_first
        if self.__is_online:
            self.wait()
        else:
            self.run()

    def wait(self):
        self.set_up()
        self.socket = Server(self.__board_size, self.__is_player_first)
        self.socket.start()
        self.server_timer = QBasicTimer()
        self.server_timer.start(500, self)
        self.__current_title = "Waiting For Second Player To Connect\n" \
                               f"(Your IP: {self.socket.ip})"
        label = QLabel(self)
        corgi = QMovie('images/BigCorgi.gif')
        size = self.HEIGHT - self.UPPER_SHIFT
        corgi.setScaledSize(QSize(size, size))
        corgi.start()
        label.setMovie(corgi)
        label.move((self.WIDTH - size) / 2, (self.HEIGHT - size))
        label.show()

        def back_function():
            label.hide()
            self.first()
        back = self.create_back_button(back_function)

    def timerEvent(self, event):
        if self.socket.is_connected:
            self.server_timer.stop()
            self.run()

    def ip(self):
        self.set_up()
        self.__current_title = 'Enter Host IP'
        address = QLineEdit(self)
        address.setGeometry((self.WIDTH - 300) / 2, self.UPPER_SHIFT + self.BUTTON_SIZE- self.BETWEEN_SHIFT, 300, 50)
        address.setStyleSheet('background: white;')
        address.setFont(self.__font)
        address.textChanged[str].connect(self.change_ip)
        address.show()
        enter = self.create_button('Enter', address.x(), self.UPPER_SHIFT + self.BUTTON_SIZE + self.BETWEEN_SHIFT,
                                   self.enter_ip, 300)

        def back_function():
            address.hide()
            self.host_join()
            self.ip_error = False
        back = self.create_back_button(back_function)

    def change_ip(self, text):
        self.ip_error = False
        self.update()
        self.__ip = text

    def enter_ip(self,):
        self.socket = Client(self.__ip)
        if self.socket.connect_to_server():
            self.__board_size = self.socket.board_size
            self.__is_player_first = self.socket.me_first
            self.ip_error = False
            self.run()
        else:
            self.ip_error = True
            self.update()

    def pvp_pve(self):
        self.set_up()
        self.__current_title = 'Choose Game Mode'
        x = (self.WIDTH - 300) / 2
        pvp = self.create_button("Player Vs Player", x, self.UPPER_SHIFT, self.choose_size, 300)
        pve = self.create_button("Player Vs Bot", x, pvp.y() + self.BETWEEN_SHIFT + self.BUTTON_SIZE, self.bot, 300)
        back = self.create_back_button(self.new_load)

    def bot(self):
        self.set_up()
        self.__current_title = "Choose Bot's Difficulty"
        easy = self.create_button("Easy", self.BUTTON_SIZE / 2 + self.SIDE_SHIFT,
                                  self.ONE_LINE_UPPER_SHIFT, partial(self.make_bot, 0))
        medium = self.create_button("Normal", self.BUTTON_SIZE * 3 / 2 + self.SIDE_SHIFT + self.BETWEEN_SHIFT * 3 / 2,
                                    self.ONE_LINE_UPPER_SHIFT, partial(self.make_bot, 1))
        hard = self.create_button("Hard", self.BUTTON_SIZE * 5 / 2 + self.SIDE_SHIFT + self.BETWEEN_SHIFT * 3,
                                  self.ONE_LINE_UPPER_SHIFT, partial(self.make_bot, 2))
        back = self.create_back_button(self.pvp_pve)

    def make_bot(self, difficulty):
        self.__is_bot_active = True
        self.__bot_difficulty = difficulty
        self.choose_size()

    def load(self):
        folder = 'online' if self.__is_online else 'offline'
        name = QFileDialog.getOpenFileName(self, 'Chose Save File', f'saves/{folder}/', 'Save Files (*.save)')[0]
        if name == '':
            return
        GameWindow(False, name, self.__is_online, self.socket)
        self.hide()

    def run(self):
        GameWindow(True, self.__board_size, self.__is_bot_active, self.__is_player_first, self.__bot_difficulty,
                   self.__is_online, self.socket)
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.begin(self)
        painter.setFont(self.__font)

        self.draw_title(painter)
        self.draw_controls(painter)

        painter.end()

    def draw_title(self, painter):
        painter.drawText(0, 0, self.WIDTH, self.UPPER_SHIFT, Qt.AlignCenter | Qt.AlignVCenter, self.__current_title)
        if self.ip_error:
            pen = painter.pen()
            painter.setPen(QPen(QColor('#ff0000')))
            painter.drawText(0, self.UPPER_SHIFT / 2 + 10, self.WIDTH, self.UPPER_SHIFT, Qt.AlignCenter | Qt.AlignVCenter,
                             'Failed to connect')
            painter.setPen(pen)

    def draw_controls(self, painter):
        for button in self.__controls:
            painter.drawImage(button.x(), button.y(),
                              QImage(f'images/{button.text()}.png').scaled(button.width(), button.height()))
            exceptions = ['Enter']
            text = "" if button.text() in exceptions else button.text()
            painter.drawText(button.x() - button.width() / 2,
                             button.y(), button.width() * 2, button.height() + 30,
                             Qt.AlignCenter | Qt.AlignBottom, text)
