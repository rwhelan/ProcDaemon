import os
import select
import json

from includes import asynclient
from proc import Process

class Client(asynclient):
    def __init__(self, g, sock, addr):
        self.g = g

        self.sock = sock
        self.addr = addr
        self.sockfd = self.sock.fileno()

        self.reg_fd(self.sockfd)

        self.stdoutbuf = ''
        self.stderrbuf = ''


    def _sock_recv(self, fd, event):
        self.cmd = self.sock.recv(4096)
        if self.cmd:
            self.proc = Process(self.cmd)

            self.reg_fd(self.proc.stdout)
            self.reg_fd(self.proc.stderr)

            self.g['pids'][self.proc.pid] = self
        else:
            self.un_reg_fd(fd)
            self.sock.close()
            
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

        self.un_reg_fd(fd)

        os.close(fd)

    def proc_finish(self, code, res):

        proc_usage = {}
        for rsrc in [i for i in dir(res) if i.startswith('ru_')]:
            proc_usage[rsrc] = getattr(res, rsrc)

        response = { 'stdout'     : self.stdoutbuf,
                     'stderr'     : self.stderrbuf,
                     'returncode' : code >> 8,
                     'killsig'    : code & 255,
                     'resource'   : proc_usage,
                   }

        self.sock.send(json.dumps(response, indent = 4))

        del self.g['pids'][self.proc.pid]
        self.un_reg_fd(self.sockfd)
        self.sock.close()
