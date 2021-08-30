import abc
import time
import serial
import threading
import src.Drivers.AbstractBaseClasses as base


class Center(serial.Serial, base.AbstractPressureSensor, abc.ABC):
    def __init__(self, port,  *args, **kwargs):
        super().__init__(port, timeout=1.5, baudrate=9600)
        self.com_lock = threading.Lock()
        time.sleep(1)
        with self.com_lock:
            self.write('UNI,0\n'.encode())
            self.readline()
            self.write('\x05\n'.encode())
            self.readline()

    def read_pressure(self, channel):
        with self.com_lock:
            self.write('PR{:d}\n'.format(channel).encode())
            self.readline()
            self.write('\x05\n'.encode())
            answer = self.readline().decode().split(',')
            if answer[0] == '0':
                return float(answer[1])


class CenterOne(Center):
    def __init__(self, port):
        super().__init__(port)

    @property
    def channels(self):
        return 1


class CenterTwo(Center):
    def __init__(self, port):
        super().__init__(port)

    @property
    def channels(self):
        return 2


class CenterThree(Center):
    def __init__(self, port):
        super().__init__(port)

    @property
    def channels(self):
        return 3
