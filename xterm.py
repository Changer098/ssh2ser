# A whole lotta help http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html

import pty


class Xterm(pty.BasePty):
    cursorPositionX = 0
    cursorPositionY = 0
    file = None
    currentLine = 0
    lines = []
    file = None

    def __init__(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        super().__init__(channel, term, width, height, pixelwidth, pixelheight, modes)
        self.lines.append("")
        self.file = self.channel.makefile("rwU")

    def resize(self, width, height, pixelwidth, pixelheight):
        pass

    def send(self, value):
        if isinstance(value, bytes):
            value = bytes.decode(value, "ascii")
        # if currentline is empty, overwrite line
        # else add value to current line based on cursor position
        if len(self.lines[self.currentLine]) == 0:
            self.lines[self.currentLine] = self.lines[self.currentLine] + value
            self.channel.send(value)
            # self.cursorPositionX = self.cursorPositionX + len(value)
            self.updateCursor(self.cursorPositionX + len(value))
        else:
            if self.cursorPositionX == 0:
                # far left
                newLine = self.lines[self.currentLine]
                newLine = value + newLine
                self.lines[self.currentLine] + value
                # self.cursorPositionX = self.cursorPositionX + 1
                # move cursor left
                # self.channel.send("\u001b[{}G".format(self.cursorPositionX + 1))
                self.updateCursor(self.cursorPositionX + 1)
            elif self.cursorPositionX == len(self.lines[self.currentLine]):
                # far right, same as easy insert
                self.updateLine(self.lines[self.currentLine] + value)
                # self.cursorPositionX = self.cursorPositionX + len(value)
                self.updateCursor(self.cursorPositionX + len(value))
            else:
                # middle
                left = self.lines[self.currentLine][0:self.cursorPositionX]
                right = self.lines[self.currentLine][self.cursorPositionX:]
                newLine = left + value + right
                self.updateLine(newLine)
                # self.cursorPositionX = self.cursorPositionX + 1
                self.updateCursor(self.cursorPositionX + 1)

    def sendLine(self, line):
        self.send(line)
        self.newline()

    def newline(self):
        # Creates a new line and sets cursor position
        self.lines.append("")
        self.channel.send("\r\n")
        self.updateCursor(0)
        self.cursorPositionY = self.cursorPositionY + 1
        self.currentLine = self.currentLine + 1

    def left(self):
        if self.cursorPositionX != 0:
            # move cursor left by one
            # self.channel.send("\u001b[1D")
            # self.cursorPositionX = self.cursorPositionX - 1
            self.updateCursor(self.cursorPositionX - 1)
        else:
            self.bell()

    def right(self):
        if self.cursorPositionX != len(self.lines[self.currentLine]):
            # self.channel.send("\u001b[1C")
            # self.cursorPositionX = self.cursorPositionX + 1
            self.updateCursor(self.cursorPositionX + 1)
        else:
            self.bell()

    def bell(self):
        # self.file.write(chr(7))
        # self.file.flush()
        self.channel.send('\a')
        pass

    def backspace(self):
        # if len is 0 or cursor is at 0, send bell
        # else remove character within string at position
        if len(self.lines[self.currentLine]) == 0 or self.cursorPositionX == 0:
            self.bell()
        else:
            if self.cursorPositionX == len(self.lines[self.currentLine]):
                # right
                newLine = self.lines[self.currentLine][0:len(self.lines[self.currentLine]) - 1]
                self.updateLine(newLine)
                # self.cursorPositionX = self.cursorPositionX + 1
                self.updateCursor(self.cursorPositionX - 1)
            else:
                # middle
                left = self.lines[self.currentLine][0:self.cursorPositionX]
                right = self.lines[self.currentLine][self.cursorPositionX:]
                newLine = left[0:len(left)-1] + right
                self.updateLine(newLine)
                self.updateCursor(self.cursorPositionX - 1)

    def clear(self):
        self.channel.send("\u001b[2J")

    def clearLine(self):
        self.channel.send("\u001b[2K")
        self.channel.send("\u001b[0G")

    def readKey(self):
        return self.file.read(1)

    def updateCursor(self, newX):
        self.cursorPositionX = newX
        self.channel.send("\u001b[{}G".format(newX + 1))

    def updateLine(self, newLine):
        self.clearLine()
        self.channel.send(newLine)
        self.lines[self.currentLine] = newLine