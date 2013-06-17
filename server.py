import socket
import select

from includes import asynclient
from client import TCPClient

class TCPServer(asynclient):
    def __init__(self, g, addr, port, outstanding = 5):
        self.g = g

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((addr, port))
        self.sock.listen(outstanding)

        self.sockfd = self.sock.fileno()

        self.reg_fd(self.sockfd)

    def handle_event(self, fd, event):
        assert fd == self.sockfd
        assert event == select.EPOLLIN

        self._sock_recv(fd, event)

    def _sock_recv(self, fd, event):
        TCPClient(self.g, *self.sock.accept())
