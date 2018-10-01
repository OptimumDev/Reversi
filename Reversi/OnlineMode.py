#!/usr/bin/env python3


import socket
import ipaddress
import re
from Game import Game
from Point import Point
from PyQt5.QtCore import QThread


class OnlineMode:

    @staticmethod
    def make_turn(online_socket, game, game_window, turn):
        try:
            color = Game.WHITE if game.is_white_turn else Game.BLACK
            if turn is None:
                message = 'pass'
                game_window.log(f"Player's turn\t({color}): passed")
                game.pass_turn()
            else:
                message = str(turn)
                game_window.log(f"Player's turn\t({color}): placed checker at {turn}")
                game.make_turn(turn)
                game_window.remove_button(turn)
            online_socket.client_socket.send(bytes(message, Server.ENCODING))
            game_window.hide_buttons()
        except ConnectionError:
            game_window.connection_lost = True

    @staticmethod
    def wait_for_turn(online_socket, game, game_window):
        try:
            color = Game.WHITE if game.is_white_turn else Game.BLACK
            answer = online_socket.client_socket.recv(1024).decode()
            if answer == 'pass':
                game_window.log(f"Player's turn\t({color}): passed")
                game.pass_turn()
            else:
                turn = Point.from_string(answer)
                game_window.log(f"Player's turn\t({color}): placed checker at {turn}")
                game.make_turn(turn)
                game_window.remove_button(turn)
            game_window.highlight_buttons()
        except ConnectionError:
            game_window.connection_lost = True


class Server(QThread):
    PORT = 37001
    ENCODING = 'utf-8'

    def __init__(self, board_size, me_first, is_new, load_data):
        super().__init__()
        self.is_connected = False

        self.board_size = board_size
        self.me_first = me_first
        self.is_new = is_new
        self.load_data = load_data

        self.ip = socket.gethostbyname(socket.getfqdn())
        self.server_socket = socket.socket()
        self.server_socket.bind(('', self.PORT))
        self.server_socket.listen(1)

    def run(self):
        self.client_socket, self.client_address = self.server_socket.accept()
        message = f'{self.board_size}, {int(not self.me_first)}, {int(self.is_new)}, [{self.load_data}]'
        self.client_socket.send(bytes(message, self.ENCODING))
        self.is_connected = True

    def make_turn(self, game, game_window, turn=None):
        OnlineMode.make_turn(self, game, game_window, turn)

    def wait_for_turn(self, game, game_window):
        OnlineMode.wait_for_turn(self, game, game_window)


class Client:

    INFO_PARSER = re.compile(r'(?P<board_size>\d+), (?P<me_first>\d), (?P<is_new>\d), \[(?P<load_data>.*)\]', re.DOTALL)

    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client_socket = socket.socket()

    def connect_to_server(self):
        if not self.check_ip():
            return False
        try:
            self.client_socket.settimeout(1)
            self.client_socket.connect((self.server_ip, Server.PORT))
            self.client_socket.settimeout(None)
            game_info = self.client_socket.recv(1024)
            info = self.INFO_PARSER.search(game_info.decode())
            self.board_size = int(info['board_size'])
            self.me_first = bool(int(info['me_first']))
            self.is_new = bool(int(info['is_new']))
            self.load_data = info['load_data']
        except (TimeoutError, OSError):
            return False
        else:
            return True

    def check_ip(self):
        try:
            ipaddress.ip_address(self.server_ip)
        except ValueError:
            return False
        else:
            return True

    def make_turn(self, game, game_window, turn=None):
        OnlineMode.make_turn(self, game, game_window, turn)

    def wait_for_turn(self, game, game_window):
        OnlineMode.wait_for_turn(self, game, game_window)
