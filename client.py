import os
import select

from proc import Process

class Client(object):
    def __init__(self, g, sock, addr):
        self.g = g

        self.sock = sock
        self.addr = addr
        self.sockfd = self.sock.fileno()

        self.g['fds'][self.sockfd] = self

        self.g['poller'].register(self.sockfd, select.EPOLLIN)

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

            self.g['poller'].register(self.proc.stdout, select.EPOLLIN)
            self.g['poller'].register(self.proc.stderr, select.EPOLLIN)

            self.g['fds'][self.proc.stdout] = self
            self.g['fds'][self.proc.stderr] = self

            self.g['pids'][self.proc.pid] = self
            
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

        self.g['poller'].unregister(fd)
        del self.g['fds'][fd]

        os.close(fd)

    def proc_finish(self, code, res):
        self.sock.send(self.stdoutbuf)

        del self.g['pids'][self.proc.pid]
        
        self.sock.close()
