from device import DeviceSerial, DeviceNet, DeviceError
from config import Config
from print_ import oprint, qprint, eprint, dprint

from collections import OrderedDict
import threading


class DevsError(Exception):
    """Errors that we want to report to the user and keep running."""
    pass


class Devs:
    """List of known devices."""

    def __init__(self, config):
        self._devices = []
        self._default_dev = None
        self._config = config


    def default_device(self, index=None, name=None):
        if index:
            try:
                if self._devices[index-1]: self._default_dev = self._devices[index-1]
            except:
                pass
        if name:
            self._default_dev = self.find_device_by_name(name)
        if not self._default_dev:
            raise DevsError("no board connected")
        return self._default_dev


    def devices(self):
        for dev in self._devices:
            if dev:
                yield dev


    def find_device_by_name(self, name):
        """Find board by name."""
        for d in self._devices:
            if d.name == name: return d
        return self._default_dev_device()


    def find_serial_device_by_port(self, port):
        """Find board by port name."""
        for dev in self._devices:
            if dev.is_serial_port(port):
                return dev
        return None


    def num_devices(self):
        return sum(x is not None for x in self._devices)


    def connect_serial(self, port, board_name=None):
        """Connect to MicroPython board plugged into the specfied port."""
        qprint("Connecting via serial to {} ...".format(port))
        dev = DeviceSerial(port, self._config, board_name)
        self.add_device(dev)


    def connect_telnet(self, ip_address, board_name=None):
        """Connect to MicroPython board at specified IP address."""
        qprint("Connecting via telnet to {}' ...".format(ip_address))
        dev = DeviceNet(ip_address, self._config, board_name)
        self.add_device(dev)


    def add_device(self, dev):
        """Adds a device to the list of devices we know about."""
        self._devices.append(dev)
        if not self._default_dev:  self._default_dev = dev


    def get_dev_and_path(self, filename):
        """Determines if a given file is located locally or remotely. We assume
           that any directories from the pyboard take precendence over local
           directories of the same name. /dev_name/path where dev_name is the name of a
           given device is also considered to be associaed with the named device.

           If the file is associated with a remote device, then this function
           returns a tuple (dev, dev_filename) where dev is the device and
           dev_filename is the portion of the filename relative to the device.

           If the file is not associated with the remote device, then the dev
           portion of the returned tuple will be None.
        """
        if self._default_dev and self._default_dev.is_root_path(filename):
            return (self._default_dev, filename)
        test_filename = filename + '/'
        for dev in self._devices:
            if test_filename.startswith(dev.name()):
                dev_filename = filename[len(dev.name())-1:]
                if dev_filename == '':
                    dev_filename = '/'
                return (dev, dev_filename)
        return (None, filename)