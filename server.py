import socket
import select

from client import Client

class TCPServer(object):
    def __init__(self, g, addr, port, outstanding = 5):
        self.g = g

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((addr, port))
        self.sock.listen(outstanding)

        self.g['fds'][self.sock.fileno()] = self

        self.g['poller'].register(self.sock.fileno(), select.EPOLLIN)

    def handle_event(self, fd, event):
        if event & select.EPOLLIN:
            Client(self.g, *self.sock.accept())
