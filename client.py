import os
import select

from proc import Process

class Client(object):
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.sockfd = self.sock.fileno()

        clients.append(self)
        self.fds = [self.sockfd]

        poller.register(self.sockfd, select.EPOLLIN)

        self.stdoutbuf = ''
        self.stderrbuf = ''

    def handle_event(self, fd, event):
        if event & select.EPOLLIN:
            if fd == self.sockfd:
                self._sock_recv(fd, event)
            else:
                self._proc_recv(fd, event)

        if event & select.EPOLLHUP:
            if fd == self.sockfd:
                self._sock_hup(fd, event)
            else:
                self._proc_hup(fd, event)

    def _sock_recv(self, fd, event):
        self.cmd = self.sock.recv(4096)
        if self.cmd:
            self.proc = Process(self.cmd)

            poller.register(self.proc.stdout, select.EPOLLIN)
            poller.register(self.proc.stderr, select.EPOLLIN)

            self.fds.append(self.proc.stdout)
            self.fds.append(self.proc.stderr)
            
    def _sock_hup(self, fd, event):
        raise NotImplementedError('Client._sock_hup')

    def _proc_recv(self, fd, event):
        if fd == self.proc.stdout:
            # Someday I'll use mutible data types...
            self.stdoutbuf += os.read(fd, 4096)
        elif fd == self.proc.stderr:
            self.stderrbuf += os.read(fd, 4096)

    def _proc_hup(self, fd, event):
        self._proc_recv(fd, event)

        poller.unregister(fd)
        self.fds.remove(fd)

        os.close(fd)
