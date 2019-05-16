class BasePty:
    channel = None
    term = None
    dimensions = [0, 0]
    pixelDimensions = [0, 0]
    modes = None

    def __init__(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        self.channel = channel
        self.term = term
        self.dimensions[0] = width
        self.dimensions[1] = height
        self.pixelDimensions[0] = pixelwidth
        self.pixelDimensions[1] = pixelheight
        self.modes = modes

    def resize(self, width, height, pixelwidth, pixelheight):
        self.dimensions[0] = width
        self.dimensions[1] = height
        self.pixelDimensions[0] = pixelwidth
        self.pixelDimensions[1] = pixelheight


# Allow peeking and consuming read data
class KeyHistory:
    queue = None

    def __init__(self):
        self.queue = list()

    def add(self, key):
        self.queue.append(key)

    def empty(self):
        return len(self.queue) == 0

    def peek(self):
        pass

    # consume a key (or multiple keys) from the history
    # returns a key if consuming a single key
    # returns an array of keys if consuming multiple keys
    def consume(self, count=1):
        pass


# a tuple describing a read key
class Key:
    raw_key = None
    int_key = None

    def __init__(self, raw_key, int_key):
        self.raw_key = raw_key
        self.int_key = int_key
