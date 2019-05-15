import serial
import os
import sys
import termios
import threading
import tty

old = None
encoding = "ascii"

def isAdmin():
    return os.getuid() == 0


def setup():
    global old
    old = termios.tcgetattr(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())


def restore():
    global old
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


# serial->stdout
def reader(ser):
    while True:
        try:
            if ser.in_waiting > 0:
                # print("WAITING", end='', flush=True)
                # new data to read
                serialLine = ser.read(1)
                print(serialLine.decode(encoding), end='', flush=True)
                # print(serialLine, end='', flush=True)
                ser.flush()
        except KeyboardInterrupt:
            print("Killing from reader")
            return


# stdin->serial
def writer(ser):
    while True:
        try:
            c = sys.stdin.read(1)
            # print("Read {0}".format(c), end='', flush=True)
            # print("wrote {}".format(c))
            # print("w: {0}".format(c, end=', ', flush=True))
            if c == '\n':
                ser.write(b'\r')
            else:
                ser.write(c.encode(encoding))
            ser.flush()
        except KeyboardInterrupt:
            print("Killing from writer")
            return
        except:
            pass


if not isAdmin():
    print("only root can run this script")
    sys.exit(-1)

setup()
try:
    ser = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    # ser.write(b'\r\n')
    ser.flush()
    kill = False
    readerThread = threading.Thread(target=reader, args=[ser])
    writerThread = threading.Thread(target=writer, args=[ser])
    readerThread.daemon = True
    writerThread.daemon = True
    writerThread.start()
    readerThread.start()
except:
    restore()


try:
    writerThread.join()
except KeyboardInterrupt:
    kill = True
    restore()
    print("Killing from main")