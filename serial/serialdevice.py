from enum import Enum
import os
import traceback

DeviceType = Enum('DeviceType', 'USBSerial USB UNKNOWN')


class SerialDevice:
    isUSB = False
    friendly_name = None            # recognizable name assigned in config
    device_info = None
    device_path = None
    device_type = None
    device_int = None

    def __init__(self, device_int):
        self.device_int = device_int
        self.device_path = os.path.realpath('/sys/class/tty/{}/device'.format(os.path.basename(self.device_int)))
        self.device_type = self.get_device_type(self.device_path)
        self.device_info = DeviceInfo()
        self.isUSB = self.device_type == DeviceType.USBSerial or self.device_type == DeviceType.USB
        usb_interface_path = None
        if self.device_type == DeviceType.USBSerial:
            usb_interface_path = os.path.dirname(self.device_path)
        elif self.device_type == DeviceType.USB:
            usb_interface_path = self.device_path
        if usb_interface_path is not None:
            usb_interface_path = os.path.dirname(usb_interface_path)
            try:
                self.device_info.int_count = self.read_file(usb_interface_path, "bNumInterfaces")
                if self.device_info.int_count is not None:
                    self.device_info.int_count = int(self.device_info.int_count)
                self.device_info.vendor_id = self.read_file(usb_interface_path, "idVendor")
                self.device_info.product_id = self.read_file(usb_interface_path, "idProduct")
                # Serial number doesn't show on ubuntu 19.04
                # self.device_info.serial_num = self.read_file(usb_interface_path, "serial")
                self.device_info.manufacturer = self.read_file(usb_interface_path, "manufacturer")
                self.device_info.product = self.read_file(usb_interface_path, "product")
            except Exception as e:
                print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
                traceback.print_exc()

    @staticmethod
    def get_device_type(device_path):
        subsystem = os.path.basename(os.path.realpath(os.path.join(device_path, 'subsystem')))
        if subsystem == 'usb-serial':
            return DeviceType.USBSerial
        elif subsystem == 'usb':
            return DeviceType.USB
        return DeviceType.UNKNOWN

    @staticmethod
    def read_file(folder, file):
        try:
            f = open(os.path.join(folder, file), "r")
            return f.readline().strip('\n')
        except Exception as e:
            print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
            traceback.print_exc()
            return None

    def __str__(self):
        return self.device_info.get_prod_name()


class DeviceInfo:
    manufacturer = None
    int_count = 0
    vendor_id = None
    product_id = None
    serial_num = None
    product = None

    def get_prod_name(self):
        return self.product
