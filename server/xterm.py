# A whole lotta help http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html

import server


class Xterm(server.pty.BasePty):
    cursorPositionX = 0
    cursorPositionY = 0
    file = None
    currentLine = 0
    lines = []
    lockedX = False
    lockedY = False
    reader = None
    editableX = 0       # Allow cursor movement in editable zone
    editableLocked = False

    def __init__(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        super().__init__(channel, term, width, height, pixelwidth, pixelheight, modes)
        self.lines.append("")
        self.reader = server.pty.KeyReader(self.channel.makefile("r"))

    def cleanup(self):
        self.currentLine = 0
        self.lines.clear()
        self.lockedY = False
        self.lockedX = False
        self.cursorPositionX = 0
        self.cursorPositionY = 0
        self.reader = None
        self.editableX = 0
        self.editableLocked = False

    def resize(self, width, height, pixelwidth, pixelheight):
        pass

    def send(self, value):
        if isinstance(value, bytes):
            value = bytes.decode(value, "ascii")
        if isinstance(value, server.Key):
            value = value.c()
        # if currentline is empty, overwrite line
        # else add value to current line based on cursor position
        if len(self.lines[self.currentLine]) == 0:
            self.lines[self.currentLine] = self.lines[self.currentLine] + value
            self.channel.send(value)
            # self.cursorPositionX = self.cursorPositionX + len(value)
            self.update_cursor(newX=self.cursorPositionX + len(value))
        else:
            if self.cursorPositionX == 0:
                # far left
                new_line = self.lines[self.currentLine]
                new_line = value + new_line
                self.lines[self.currentLine] = value
                # self.cursorPositionX = self.cursorPositionX + 1
                # move cursor left
                # self.channel.send("\u001b[{}G".format(self.cursorPositionX + 1))
                self.update_cursor(newX=self.cursorPositionX + 1)
            elif self.cursorPositionX == len(self.lines[self.currentLine]):
                # far right, same as easy insert
                self.update_line(self.lines[self.currentLine] + value)
                # self.cursorPositionX = self.cursorPositionX + len(value)
                self.update_cursor(newX=self.cursorPositionX + len(value))
            else:
                # middle
                left = self.lines[self.currentLine][0:self.cursorPositionX]
                right = self.lines[self.currentLine][self.cursorPositionX:]
                new_line = left + value + right
                self.update_line(new_line)
                # self.cursorPositionX = self.cursorPositionX + 1
                self.update_cursor(newX=self.cursorPositionX + 1)

    def send_line(self, line):
        self.send(line)
        self.newline()

    def newline(self):
        # Creates a new line and sets cursor position
        self.lines.append("")
        self.channel.send("\r\n")
        self.update_cursor(newX=0)
        self.cursorPositionY = self.cursorPositionY + 1
        self.currentLine = self.currentLine + 1

    def left(self):
        if self.lockedX:
            self.bell()
        elif self.editableLocked:
            if self.cursorPositionX <= self.editableX:
                self.bell()
            else:
                self.update_cursor(newX=self.cursorPositionX - 1)
        elif self.cursorPositionX != 0:
            # move cursor left by one
            # self.channel.send("\u001b[1D")
            # self.cursorPositionX = self.cursorPositionX - 1
            self.update_cursor(newX=self.cursorPositionX - 1)
        else:
            self.bell()

    def right(self):
        if self.lockedX:
            self.bell()
        elif self.cursorPositionX != len(self.lines[self.currentLine]):
            # self.channel.send("\u001b[1C")
            # self.cursorPositionX = self.cursorPositionX + 1
            self.update_cursor(newX=self.cursorPositionX + 1)
        else:
            self.bell()

    def up(self):
        if self.lockedY:
            self.bell()
        elif self.cursorPositionY != 0:
            self.update_cursor(newY=self.cursorPositionY - 1)
            # check new position is within x bounds
            if self.cursorPositionX > len(self.lines[self.currentLine]):
                self.update_cursor(newX=len(self.lines[self.currentLine]))
        else:
            self.bell()

    def down(self):
        if self.lockedY:
            self.bell()
        elif self.cursorPositionY != len(self.lines) - 1:
            self.update_cursor(newY=self.cursorPositionY + 1)
            # check new position is within x bounds
            if self.cursorPositionX > len(self.lines[self.currentLine]):
                self.update_cursor(newX=len(self.lines[self.currentLine]))
        else:
            self.bell()

    def bell(self):
        self.channel.send('\a')
        pass

    def backspace(self):
        # if len is 0 or cursor is at 0, send bell
        # else remove character within string at position
        if len(self.lines[self.currentLine]) == 0 or self.cursorPositionX == 0:
            self.bell()
        else:
            if self.editableX:
                if self.cursorPositionX <= self.editableX:
                    self.bell()
                    return
            if self.cursorPositionX == len(self.lines[self.currentLine]):
                # right
                new_line = self.lines[self.currentLine][0:len(self.lines[self.currentLine]) - 1]
                self.update_line(new_line)
                # self.cursorPositionX = self.cursorPositionX + 1
                self.update_cursor(self.cursorPositionX - 1)
            else:
                # middle
                left = self.lines[self.currentLine][0:self.cursorPositionX]
                right = self.lines[self.currentLine][self.cursorPositionX:]
                new_line = left[0:len(left)-1] + right
                self.update_line(new_line)
                self.update_cursor(self.cursorPositionX - 1)

    def clear(self):
        self.channel.send("\u001b[0;0H")        # Set cursor to 0,0
        self.channel.send("\u001b[2J")          # erase screen
        self.cursorPositionX = 0
        self.cursorPositionY = 0

    def clear_line(self):
        self.channel.send("\u001b[2K")
        self.channel.send("\u001b[0G")
        self.lines[self.currentLine] = ""

    def read_key(self):
        # raw_key = self.file.read(1)
        # return raw_key, int.from_bytes(raw_key, 'big')
        return self.reader.consume()

    def lock(self, x=False, y=False):
        if x:
            self.lockedX = True
        if y:
            self.lockedY = True

    def unlock(self, x=False, y=False):
        if x:
            self.lockedX = False
        if y:
            self.lockedY = False

    def update_cursor(self, newX=None, newY=None):
        if newX is not None:
            self.cursorPositionX = newX
            self.channel.send("\u001b[{}G".format(newX + 1))  # set cursor to new position
        if newY is not None:
            self.cursorPositionY = newY
            self.channel.send("\u001b[{};{}H".format(newY + 1, self.cursorPositionX + 1))
            self.currentLine = newY

    def update_line(self, new_line):
        self.clear_line()
        self.channel.send(new_line)
        self.lines[self.currentLine] = new_line

    def close(self):
        self.cleanup()
        self.channel.close()

    # Matching keys
    def arrow(self, key):
        if key == 27:
            # peek key
            # if key == 91
            # peek key
            # if key is in [65,66,67,68] consume all three keys
            if self.reader.peek() == 91:
                peeked = self.reader.peek()
                if peeked == 65:
                    self.reader.consume(count=2)
                    self.up()
                    return True
                elif peeked == 66:
                    self.reader.consume(count=2)
                    self.down()
                    return True
                elif peeked == 67:
                    self.reader.consume(count=2)
                    self.right()
                    return True
                elif peeked == 68:
                    self.reader.consume(count=2)
                    self.left()
                    return True
                else:
                    return False
        else:
            return False

    def ctrlc(self, key):
        return key == 3

    def enter(self, key, is_input=False):
        if self.editableLocked and not is_input:
            # ignore enter so that inputKey can grab it
            return False
        return key == 13

    def back(self, key):
        return key == 127

    def match(self, key, code):
        return key == code

    # Input
    def input(self, prompt):
        self.lock(y=True)
        self.editableLocked = True
        self.send(prompt)
        self.editableX = len(prompt)

    def input_key(self, key, only_numbers=False):
        if self.enter(key, is_input=True):
            # get inputted value and return it
            return self.lines[self.currentLine][self.editableX:]
        else:
            # apply modifiers
            if only_numbers:
                if server.RE_CharIsNum.match(key.c()) is not None:
                    self.send(key)
                # only send if key matches modifier
            else:
                self.send(key)
            return None

    def input_fail(self, error_msg):
        # copy current line minus invalid input
        line_copy = self.lines[self.currentLine][0:self.editableX]
        self.clear_line()
        self.send_line(error_msg)
        self.send(line_copy)

    def input_success(self, no_newline=False):
        self.lock(y=False)
        self.editableLocked = False
        self.editableX = 0
        if not no_newline:
            self.newline()

    def button(self, message):
        return "\u001b[7m[{}]\u001b[0m".format(message)
