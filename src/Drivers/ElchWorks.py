import src.Drivers.Aera
import src.Drivers.AbstractBaseClasses as base
import serial
import threading


class Valvolino(serial.Serial, base.AbstractValveController):
    """Driver class for Valvolino Controller"""
    def __init__(self, port):
        super().__init__(port=port, timeout=0.5, baudrate=9600)
        self.channels = 4
        self.com_lock = threading.Lock()

    def switch_valve(self, channel, state):
        """Toggle a valve"""
        assert 1 <= channel <= self.channels, 'Invalid channel'
        string = '{:02d}SSP{:1d}'.format(channel, state)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')
            self.readline()

    def read_valve_state(self, channel):
        """Read state of a valve"""
        assert 1 <= channel <= self.channels, 'Invalid channel'
        string = f'{channel:02d}RSP'
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')

            answer = self.readline()
            return bool(int(answer.decode()))


class Ventolino(src.Drivers.Aera.ROD4):
    """
    Driver class for Ventolino MFC controllers
    This is the same as Area ROD-4 since the communication protocols are iodentical.
    Separate class in case this might change
    """
    def set_flow(self, channel, flow):
        """Set desired flow"""
        assert 0 <= flow <= 100 and 1 <= channel <= self.channels, 'Invalid channel or flow'
        string = '{:02d}SFD{:3.1f}'.format(channel, flow)
        with self.com_lock:
            self.write(b'\x02')
            self.write(string.encode())
            self.write(b'\x0D')
            answer = self.readline()
            # Also accept empty string because some old thermolinos return no acknowledgment line
            assert answer.decode in ('rec', ''), 'Invalid response from ROD4'
