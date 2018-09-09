#!/usr/bin/env python3


import socket
import ipaddress


class Server:
    PORT = 37001

    def __init__(self):
        self.is_connected = False

        self.ip = socket.gethostbyname(socket.getfqdn())
        self.server_socket = socket.socket()
        self.server_socket.bind(('', self.PORT))
        self.server_socket.listen(1)

        self.client_socket, self.client_address = self.server_socket.accept()
        self.is_connected = True


class Client:

    def __init__(self, server_ip):
        self.server_ip = server_ip
        self.client_socket = socket.socket()

    def connect_to_server(self):
        if not self.check_ip():
            return False
        try:
            self.client_socket.connect((self.server_ip, Server.PORT))
        except TimeoutError:
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

