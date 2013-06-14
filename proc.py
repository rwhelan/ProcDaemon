import os
import shlex

class Process(object):
    def __init__(self, cmd, autorun = True):
        self.cmd = shlex.split(cmd)
        self.pid = 0

#        self.stdinOUT,  self.stdin = os.pipe()
        self.stdout, self.stdoutIN = os.pipe()
        self.stderr, self.stderrIN = os.pipe()

#        self.fds = ( self.stdin,
#                     self.stdout,
#                     self.stderr,
#                   )

        if autorun: self.run()

    def run(self):
        self.pid = os.fork()
        if not self.pid:
            stdin = os.open('/dev/zero', os.O_RDONLY)
            os.dup2(stdin, 0)
            os.close(stdin)

            os.dup2(self.stdoutIN, 1)
            os.dup2(self.stderrIN, 2)
            os.closerange(3, 255)

            os.execvp(self.cmd[0], self.cmd)

        os.close(self.stdoutIN)
        os.close(self.stderrIN)
