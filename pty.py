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
