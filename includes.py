import select

class asynclient(object):
#    def __init__(self, g):
#        self.g = g

    def reg_fd(self, fd, event_filter = select.EPOLLIN):
        self.g['fds'][fd] = self
        self.g['poller'].register(fd, event_filter)

    def un_reg_fd(self, fd):
        del self.g['fds'][fd]
        self.g['poller'].unregister(fd)

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
