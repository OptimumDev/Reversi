from PyQt5.QtGui import QIcon, QPainter, QFont, QImage, QMovie
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize
from functools import partial
from GameWindow import GameWindow


class SettingsWindow(QWidget):
    BUTTON_SIZE = 100
    UPPER_SHIFT = 100
    SIDE_SHIFT = 50
    BETWEEN_SHIFT = 40
    WIDTH = BUTTON_SIZE * 4 + SIDE_SHIFT * 2 + BETWEEN_SHIFT * 3
    HEIGHT = BUTTON_SIZE * 2 + UPPER_SHIFT * 2 + BETWEEN_SHIFT
    TWO_BUTTONS_POSITIONS = (SIDE_SHIFT + BETWEEN_SHIFT + BUTTON_SIZE / 2,
                             WIDTH - SIDE_SHIFT - BETWEEN_SHIFT - BUTTON_SIZE * 3 / 2)
    ONE_LINE_UPPER_SHIFT = UPPER_SHIFT * 3 / 2

    def __init__(self):
        super().__init__()

        self.__font = QFont("times", 20)

        self.__board_size = 8
        self.__is_online = False
        self.__is_player_first = True
        self.__is_bot_active = False
        self.__bot_difficulty = 1
        self.__ip = '0.0.0.0'

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

    def create_button(self, name, x, y, action, width = 100, height = 100):
        button = QPushButton(name, self)
        button.setGeometry(x, y, width, height)
        button.clicked.connect(action)
        button.setStyleSheet("background: transparent; color: transparent;")
        button.show()
        self.__controls.append(button)
        return button

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
        join = self.create_button("Join", self.TWO_BUTTONS_POSITIONS[1], host.y(), self.ip)

    def new_load(self):
        self.set_up()
        self.__current_title = 'New or Load?'
        new = self.create_button("New Game", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, self.pvp_pve)
        load = self.create_button("Load", self.TWO_BUTTONS_POSITIONS[1], new.y(), self.load)
        load.show()

    def choose_size(self):
        self.set_up()
        self.__current_title = 'Choose Size'
        for i in range(4, 9, 2):
            button = self.create_button(str(i), self.BUTTON_SIZE / 2 + self.SIDE_SHIFT +
                                        (i - 4) / 2 * (self.BUTTON_SIZE + self.BETWEEN_SHIFT * 3 / 2),
                                        self.UPPER_SHIFT,
                                        partial(self.change_size, i))
        for i in range(10, 17, 2):
            button = self.create_button(str(i),
                                        self.SIDE_SHIFT + (i - 10) / 2 * (self.BUTTON_SIZE + self.BETWEEN_SHIFT),
                                        self.UPPER_SHIFT + self.BUTTON_SIZE + self.BETWEEN_SHIFT,
                                        partial(self.change_size, i))

    def change_size(self, size):
        self.__board_size = size
        if self.__is_online or self.__is_bot_active:
            self.first()
        else:
            self.run()

    def first(self):
        self.update()
        self.__current_title = 'Who Will Be The First'
        self.__controls = []
        me = self.create_button("Me", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT,
                                partial(self.make_first, True))
        other = self.create_button("Other" if self.__is_online else "Bot", self.TWO_BUTTONS_POSITIONS[1], me.y(),
                                   partial(self.make_first, False))

    def make_first(self, me_first):
        self.__is_player_first = me_first
        if self.__is_online:
            self.wait()
        else:
            self.run()

    def wait(self):
        self.set_up()
        self.__current_title = 'Waiting For Second Player To Connect\n' \
                               '(Not ready yet, but this Puppy is amazing, isn\'t it?)'
        layout = QVBoxLayout()
        label = QLabel()
        corgi = QMovie('images/swimmingCorgi.gif')
        corgi.setScaledSize(QSize(self.HEIGHT - self.UPPER_SHIFT, self.HEIGHT - self.UPPER_SHIFT))
        corgi.start()
        label.setMovie(corgi)
        layout.addWidget(label)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignCenter)
        self.setLayout(layout)

    def ip(self):
        self.set_up()
        self.__current_title = 'Enter Host IP\n(Not ready yet) '
        address = QLineEdit(self)
        address.setGeometry((self.WIDTH - 300) / 2, self.UPPER_SHIFT + self.BUTTON_SIZE- self.BETWEEN_SHIFT,
                           300, 50)
        address.setStyleSheet('background: white;')
        address.setFont(self.__font)
        address.show()
        enter = self.create_button('Enter', address.x(), self.UPPER_SHIFT + self.BUTTON_SIZE + self.BETWEEN_SHIFT,
                                   lambda _: 0, 300)

    def enter_ip(self, address):
        self.__ip = address

    def pvp_pve(self):
        self.set_up()
        self.__current_title = 'Choose Game Mode'
        x = (self.WIDTH - 300) / 2
        pvp = self.create_button("Player Vs Player", x, self.UPPER_SHIFT, self.choose_size, 300)
        pve = self.create_button("Player Vs Bot", x, pvp.y() + self.BETWEEN_SHIFT + self.BUTTON_SIZE, self.bot, 300)

    def bot(self):
        self.set_up()
        self.__current_title = "Choose Bot's Difficulty"
        easy = self.create_button("Easy", self.BUTTON_SIZE / 2 + self.SIDE_SHIFT,
                                  self.ONE_LINE_UPPER_SHIFT, partial(self.make_bot, 0))
        medium = self.create_button("Normal", self.BUTTON_SIZE * 3 / 2 + self.SIDE_SHIFT + self.BETWEEN_SHIFT * 3 / 2,
                                    self.ONE_LINE_UPPER_SHIFT, partial(self.make_bot, 1))
        hard = self.create_button("Hard", self.BUTTON_SIZE * 5 / 2 + self.SIDE_SHIFT + self.BETWEEN_SHIFT * 3,
                                  self.ONE_LINE_UPPER_SHIFT, partial(self.make_bot, 2))

    def make_bot(self, difficulty):
        self.__is_bot_active = True
        self.__bot_difficulty = difficulty
        self.choose_size()

    def load(self):
        name = QFileDialog.getOpenFileName(self, 'Chose Save File', 'saves/', 'Reversy Save (*.rs)')[0]
        if name == '':
            return
        GameWindow(False, name)
        self.hide()

    def run(self):
        GameWindow(True, self.__board_size, self.__is_bot_active, self.__is_player_first, self.__bot_difficulty)
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

    def draw_controls(self, painter):
        for button in self.__controls:
            image = 'Online' if button.text() == 'Join' else button.text()
            image = 'Offline' if button.text() == 'Host' else image
            painter.drawImage(button.x(), button.y(),
                              QImage(f'images/{image}.png').scaled(button.width(), button.height()))
            exceptions = [str(i) for i in range(4, 17, 2)] + ['Enter']
            text = "" if button.text() in exceptions else button.text()
            painter.drawText(button.x() - button.width() / 2,
                             button.y(), button.width() * 2, button.height() + 30,
                             Qt.AlignCenter | Qt.AlignBottom, text)
