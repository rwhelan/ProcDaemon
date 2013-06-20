
from includes import g
from core import asyncloop
from server import TCPServer

TCPServer(g, '127.0.0.1', 19191)

asyncloop(g)
