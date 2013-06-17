import select

class asynclient(object):
    def reg_fd(self, fd, event_filter = select.EPOLLIN):
        self.g['fds'][fd] = self
        self.g['poller'].register(fd, event_filter)

    def un_reg_fd(self, fd):
        del self.g['fds'][fd]
        self.g['poller'].unregister(fd)
