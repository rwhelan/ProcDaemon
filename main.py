import os
import select
import signal

from server import TCPServer

g = { 'poller'  : select.epoll(),
      'fds'     : {},
      'pids'    : {},
    }

TCPServer(g, '127.0.0.1', 19191)

def h_sigchld(sig, frm):
    pid, exitcode, res = os.wait3(os.WNOHANG)
    g['pids'][pid].proc_finish(exitcode, res)
signal.signal(signal.SIGCHLD, h_sigchld)

while True:
    try:
        for ready in g['poller'].poll():
            fd, event = ready
            print ready

            g['fds'][fd].handle_event(fd, event)

    except IOError, e:
        if e.errno == 4:
            continue
        else:
            raise
