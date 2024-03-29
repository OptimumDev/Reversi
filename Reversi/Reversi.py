#!/usr/bin/env python3


import sys
from GameWindow import GameWindow
from SettingsWindow import SettingsWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    currentExitCode = GameWindow.EXIT_CODE_CHANGE_MODE
    while currentExitCode == GameWindow.EXIT_CODE_CHANGE_MODE:
        app = QApplication(sys.argv)
        window = SettingsWindow()
        currentExitCode = app.exec_()
        app = None
    sys.exit(currentExitCode)
