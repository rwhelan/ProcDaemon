import socket
import select

from client import Client

class TCPServer(object):
    def __init__(self, addr, port, oustanding = 5):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((addr, port))
        self.sock.listen(outstanding)

        self.fds = [self.sock.fileno()]

        poller.register(self.sock.fileno(), select.EPOLLIN)
        clients.append(self)

    def handle_event(self, fd, event):
        if event & select.EPOLLIN:
            clients.append(Client(*self.sock.accept()))
