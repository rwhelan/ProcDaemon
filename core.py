import os
import signal
import errno


def asyncloop(g):

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
