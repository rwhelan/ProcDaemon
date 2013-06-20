import os
import select
import json

from includes import asynclient
from proc import Process

print_calls = True

def clgr(fn):
    def wrapper(*args):
        if print_calls: print fn
        fn(*args)
    return wrapper

class TCPClient(asynclient):
    def __init__(self, g, sock, addr):
        self.g = g

        self.sock = sock
        self.addr = addr
        self.sockfd = self.sock.fileno()

        self.reg_fd(self.sockfd)

        self.stdoutbuf = ''
        self.stderrbuf = ''
        self.splerrbuf = ''

        self.havecmd = False

    @clgr
    def _sock_recv(self, fd, event):
        self.cmd = self.sock.recv(4096)
        if self.cmd and not self.havecmd:
            self.havecmd = True

            self.proc = Process(self.cmd)

            self.reg_fd(self.proc.stdout)
            self.reg_fd(self.proc.stderr)
            self.reg_fd(self.proc.splerr)

            self.g['pids'][self.proc.pid] = self

        if not self.cmd:
            # If we're here, the client disconnected

            # Did they leave a proc running?
            if hasattr(self, 'proc'):
                self.un_reg_fd(self.proc.stdout)
                self.un_reg_fd(self.proc.stderr)
                self.un_reg_fd(self.proc.splerr)
                os.close(self.proc.stdout)
                os.close(self.proc.stderr)
                os.close(self.proc.splerr)
                os.kill(self.proc.pid, 9)

            self._close_net_sock()


    @clgr
    def _sock_hup(self, fd, event):
        raise NotImplementedError('Client._sock_hup')


    @clgr
    def _proc_recv(self, fd, event):
        try:
            if fd == self.proc.stdout:
                # Someday I'll use mutible data types...
                self.stdoutbuf += os.read(fd, 4096)
            elif fd == self.proc.stderr:
                self.stderrbuf += os.read(fd, 4096)
            elif fd == self.proc.splerr:
                self.splerrbuf += os.read(fd, 4096)

        except OSError, E:
            if E.errno != 9: # Bad file descriptor (fd closed) 
                raise


    @clgr
    def _proc_hup(self, fd, event):
        self._proc_recv(fd, event)
        self.un_reg_fd(fd)
        os.close(fd)


    @clgr
    def _close_net_sock(self):
        if not hasattr(self, 'sockclosed'):
            self.un_reg_fd(self.sockfd)
            self.sock.close()
            self.sockclosed = True


    @clgr
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


    @clgr
    def proc_finish(self, code, res):
        if not hasattr(self, 'sockclosed'):

            self._proc_recv(self.proc.splerr, None)
            self._proc_recv(self.proc.stderr, None)
            self._proc_recv(self.proc.stdout, None)

            proc_usage = {}
            for rsrc in [i for i in dir(res) if i.startswith('ru_')]:
                proc_usage[rsrc] = getattr(res, rsrc)

            response = { 'stdout'     : self.stdoutbuf,
                         'stderr'     : self.stderrbuf,
                         'strerror'   : self.splerrbuf,
                         'returncode' : code >> 8,
                         'killsig'    : code & 255,
                         'resource'   : proc_usage,
                       }

            self.sock.send(json.dumps(response, indent = 4))
            self._close_net_sock()

        del self.g['pids'][self.proc.pid]
