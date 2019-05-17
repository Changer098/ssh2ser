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
class KeyReader:
    queue = None
    peek_index = 0           # where the next peek operation will occur
    fd = None

    def __init__(self, fd):
        self.queue = list()
        self.fd = fd

    def __read(self):
        self.queue.append(Key(self.fd.read(1)))

    def __empty(self):
        return len(self.queue) == 0

    def __length(self):
        return len(self.queue)

    def __getFront(self):
        value = self.queue[0]
        self.queue.remove(value)
        return value

    def peek(self):
        # if empty, read
        if self.__empty() or self.peek_index >= self.__length():
            self.__read()
        # return queue[peekIndex]
        value = self.queue[self.peek_index]
        self.peek_index += 1
        return value

    # consume a key (or multiple keys) from the history
    # returns a key if consuming a single key
    # returns an array of keys if consuming multiple keys
    def consume(self, count=1):
        # reset peakIndex
        self.peek_index = 0
        if self.__empty():
            for i in range(0, count):
                self.__read()
        if self.__length() < count:
            # read more data to consume
            for i in range(0, count - self.__length()):
                self.__read()
        # pop from front of queue
        if count == 1:
            return self.__getFront()
        else:
            values = []
            for i in range(0, count):
                values.append(self.__getFront())
            return values


# a tuple describing a read key
class Key:
    raw_key = None
    int_key = None
    char = None

    def __init__(self, raw_key, int_key=None):
        self.raw_key = raw_key
        if int_key is None:
            self.int_key = int.from_bytes(raw_key, 'big')
        else:
            self.int_key = int_key
        self.char = chr(self.int_key)

    # overload equal operator
    def __eq__(self, other):
        if isinstance(other, Key):
            if self.raw_key != other.raw_key:
                return False
            if self.int_key != other.int_key:
                return False
            return True
        elif isinstance(other, int):
            return self.int_key == other
        else:
            raise TypeError("other is not an int or a Key")

    def c(self):
        return self.char
