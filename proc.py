import os
import shlex
import errno

class Process(object):
    def __init__(self, cmd, autorun = True):
        self.cmd = cmd
        self.pid = 0

        self.stdout, self.stdoutIN = os.pipe()
        self.stderr, self.stderrIN = os.pipe()
        self.splerr, self.splerrIN = os.pipe()

        if autorun: self.run()

    def run(self):
        self.pid = os.fork()
        if not self.pid:
            os.close(self.splerr)

            stdin = os.open('/dev/zero', os.O_RDONLY)
            os.dup2(stdin, 0)
            os.close(stdin)

            os.dup2(self.stdoutIN, 1)
            os.dup2(self.stderrIN, 2)

            os.dup2(self.splerrIN, 255)

            os.closerange(3, 255)

            try:
                _cmd = shlex.split(self.cmd)
            except ValueError, E:
                os.write(255, E.args[0])
                os.closerange(0, 256)
                os._exit(255)

            try:
                os.execvp(_cmd[0], _cmd)
            except OSError, E:
                os.write(255, E.args[1])
                os.closerange(0, 256)
                os._exit(E.errno)


                

        os.close(self.stdoutIN)
        os.close(self.stderrIN)
        os.close(self.splerrIN)
