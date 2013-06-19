import os
import select
import signal
import errno

from server import TCPServer

g = { 'poller'  : select.epoll(),
      'fds'     : {},
      'pids'    : {},
    }

TCPServer(g, '127.0.0.1', 19191)

def h_sigchld(sig, frm):
    while True:
       try:
           pid, exitcode, res = os.wait3(os.WNOHANG)
           if not pid:
               break
           g['pids'][pid].proc_finish(exitcode, res)

       except OSError, E:
           if E.errno == errno.ECHILD:
               break
           else:
               raise

signal.signal(signal.SIGCHLD, h_sigchld)

print os.getpid()
while True:
    try:
        for ready in g['poller'].poll():
            fd, event = ready

            try: g['fds'][fd].handle_event(fd, event)
            except KeyError: continue

    except IOError, e:
        if e.errno == errno.EINTR:
            continue
        else:
            raise
