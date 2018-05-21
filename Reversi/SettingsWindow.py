from PyQt5.QtGui import QIcon, QPainter, QFont, QImage, QMovie
from PyQt5.QtWidgets import QWidget, QPushButton, QDesktopWidget, QLabel, QVBoxLayout
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
        self.__box_font = QFont("times", 15)

        self.__board_size = 8
        self.__player_first = True
        self.__bot_difficulty = 1

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

        self.wait()

        # self.create_button("123", 0, 0, partial(self.run, True))

    def create_button(self, name, x, y, action, width = 100, height = 100):
        button = QPushButton(name, self)
        button.setGeometry(x, y, width, height)
        button.clicked.connect(action)
        button.setStyleSheet("background: transparent; color: transparent;")
        self.__controls.append(button)
        return button

    def starting(self):
        self.__current_title = 'Choose Game Mode'
        self.__controls = []
        offline = self.create_button("Offline", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, lambda _: 0)
        online = self.create_button("Online", self.TWO_BUTTONS_POSITIONS[1], offline.y(), lambda _: 0)

    def host_join(self):
        self.__current_title = 'Host or Join?'
        self.__controls = []
        host = self.create_button("Host", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, lambda _: 0)
        join = self.create_button("Join", self.TWO_BUTTONS_POSITIONS[1], host.y(), lambda _: 0)

    def new_load(self, is_online):
        self.__current_title = 'New or Load?'
        self.__controls = []
        new = self.create_button("New Game", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, lambda _: 0)
        load = self.create_button("Load", self.TWO_BUTTONS_POSITIONS[1], new.y(), lambda _: 0)

    def choose_size(self, is_online, is_bot):
        self.__current_title = 'Choose Size'
        self.__controls = []
        for i in range(4, 9, 2):
            button = self.create_button(str(i), self.BUTTON_SIZE / 2 + self.SIDE_SHIFT + (i - 4) / 2 * (self.BUTTON_SIZE + self.BETWEEN_SHIFT * 3 / 2),
                                        self.UPPER_SHIFT, lambda _: 0)
        for i in range(10, 17, 2):
            button = self.create_button(str(i), self.SIDE_SHIFT + (i - 10) / 2  * (self.BUTTON_SIZE + self.BETWEEN_SHIFT),
                                        self.UPPER_SHIFT + self.BUTTON_SIZE + self.BETWEEN_SHIFT, lambda _: 0)

    def first(self, is_online):
        self.__current_title = 'Who Will Be The First'
        self.__controls = []
        me = self.create_button("Me", self.TWO_BUTTONS_POSITIONS[0], self.ONE_LINE_UPPER_SHIFT, lambda _: 0)
        other = self.create_button("Other" if is_online else "Bot", self.TWO_BUTTONS_POSITIONS[1], me.y(),
                                   lambda _: 0)

    def wait(self):
        self.__current_title = 'Waiting For Second Player To Connect'
        self.__controls = []
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
        self.__current_title = 'Enter Host IP'
        self.__controls = []
        enter = self.create_button('Enter', (self.WIDTH - 300) / 2,
                                   self.UPPER_SHIFT + self.BUTTON_SIZE + self.BETWEEN_SHIFT, lambda _: 0,
                                   300, self.BUTTON_SIZE)

    def pvp_pve(self):
        self.__current_title = 'Choose Game Mode'
        self.__controls = []
        x = (self.WIDTH - 300) / 2
        pvp = self.create_button("Player Vs Player", x, self.UPPER_SHIFT, lambda _: 0, 300)
        pve = self.create_button("Player Vs Bot", x, pvp.y() + self.BETWEEN_SHIFT + self.BUTTON_SIZE, lambda _: 0, 300)

    def bot(self):
        self.__current_title = "Choose Bot's Difficulty"
        self.__controls = []
        easy = self.create_button("Easy", self.BUTTON_SIZE / 2 + self.SIDE_SHIFT,
                                  self.ONE_LINE_UPPER_SHIFT, lambda _: 0)
        medium = self.create_button("Medium", self.BUTTON_SIZE * 3 / 2 + self.SIDE_SHIFT + self.BETWEEN_SHIFT * 3 / 2,
                                    self.ONE_LINE_UPPER_SHIFT, lambda _: 0)
        hard = self.create_button("Hard", self.BUTTON_SIZE * 5 / 2 + self.SIDE_SHIFT + self.BETWEEN_SHIFT * 3,
                                  self.ONE_LINE_UPPER_SHIFT, lambda _: 0)

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

        self.draw_title(painter)
        self.draw_controls(painter)

        painter.end()

    def draw_title(self, painter):
        painter.drawText(0, 0, self.WIDTH, self.UPPER_SHIFT, Qt.AlignCenter | Qt.AlignVCenter, self.__current_title)

    def draw_controls(self, painter):
        for button in self.__controls:
            if button.text() == "Enter":
                a = 1
            image = 'Online' if button.text() == 'Join' else button.text()
            image = 'Offline' if button.text() == 'Host' else image
            painter.drawImage(button.x(), button.y(),
                              QImage(f'images/{image}.png').scaled(button.width(), button.height()))
            exceptions = [str(i) for i in range(4, 17, 2)] + ['Enter']
            text = "" if button.text() in exceptions else button.text()
            painter.drawText(button.x() - button.width() / 2,
                             button.y(), button.width() * 2, button.height() + 30,
                             Qt.AlignCenter | Qt.AlignBottom, text)
