import glob
import os
from serial import SerialDevice


def find_devices():
    devices = glob.glob("/dev/ttyUSB*")
    devices.extend(glob.glob("/dev/ttyACM*"))
    serial_devices = []
    for device in devices:
        serial_devices.append(SerialDevice(device))
    return serial_devices


def find_device(device_path):
    if os.path.exists(device_path):
        return SerialDevice(device_path)
    else:
        raise DeviceDoesNotExistException(message="{} does not exist".format(device_path))


class DeviceDoesNotExistException(BaseException):
    def __init__(self, message=None):
        super().__init__("Requested device does not exist" if message is None else message)
