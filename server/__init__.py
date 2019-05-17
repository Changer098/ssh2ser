import threading
from queue import Queue
import re

from .pty import *
from .xterm import *
from .sshserver import *
from .menu import *

QueueLock = threading.Condition()
Devices = None
ServerInfo = None

# Compiled Regexes
RE_CharIsNum = re.compile("[0-9]")
RE_CharIsLetter = re.compile("[A-z]")


class ServerQueue:
    queue = None

    def __init__(self):
        self.queue = Queue()

    def join_queue(self, obj):
        QueueLock.acquire()
        self.queue.put(obj)
        QueueLock.notify_all()

    def leave_queue(self, obj):
        QueueLock.acquire()
        self.queue.queue.remove(obj)
        QueueLock.notify_all()


class QueueObject:
    pty = None
    channel = None

    def __init__(self, pty):
        self.pty = pty


class Info:
    name = None
    banner = None

    def __init__(self, name, banner=None):
        self.name = name
        self.banner = banner
