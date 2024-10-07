import datetime
import functools as ft
import math

import serial.tools.list_ports
from PySide6.QtCore import QThreadPool
from serial import SerialException

from src.Drivers.Aera import ROD4
from src.Drivers.ElchWorks import Ventolino, Valvolino
from src.Drivers.Leybold import CenterOne, CenterTwo, CenterThree
from src.Drivers.TestDevices import *
from src.Engine.ThreadDecorators import Worker
from src.Signals import signals_engine, signals_gui

TEST_MODE = True


class MassflowControlEngine:
    def __init__(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}

        self.device_types = {'Mass Flow Controller': {'Ventolino': Ventolino, 'Area ROD-4': ROD4},
                             'Valve Controller': {'Valvolino': Valvolino},
                             'Pressure Sensor': {'Center One': CenterOne, 'Center Two': CenterTwo,
                                                 'Center Three': CenterThree}}
        if TEST_MODE:
            self.available_ports.update({'COM Test': 'Test Port'})
            self.device_types['Mass Flow Controller'].update({'Test MFC': TestMFC})
            self.device_types['Valve Controller'].update({'Test Valve Controller': TestValveController})
            self.device_types['Pressure Sensor'].update({'Test Pressure Sensor': TestPressureSensor})

        self.device_functions = {'Mass Flow Controller':
                                     {signals_gui.get_flow_is: self.get_flow_is,
                                      signals_gui.get_flow_set: self.get_flow_set,
                                      signals_gui.set_flow: self.set_flow},
                                 'Valve Controller':
                                     {signals_gui.get_valve_state: self.get_valve_state,
                                      signals_gui.set_valve_state: self.set_valve_state},
                                 'Pressure Sensor':
                                     {signals_gui.get_pressure: self.get_pressure}}

        self.devices = {key: None for key in self.device_types}

        self.is_logging = False
        self.log_start_time = None
        self.pressure_data = {channel: [] for channel in range(1, 4)}

        signals_gui.get_ports.connect(self.refresh_available_ports)
        signals_gui.get_devices.connect(self.report_devices)
        signals_gui.connect_device.connect(self.connect_device)
        signals_gui.disconnect_device.connect(self.disconnect_device)

        signals_gui.start_plot.connect(self.start_logging)
        signals_gui.clear_plot.connect(self.clear_log)
        signals_gui.export_plot.connect(self.export_log)

        self.pool = QThreadPool()

    def refresh_available_ports(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}
        if TEST_MODE:
            self.available_ports['COM Test'] = 'Test Port'
        signals_engine.answer_ports.emit(self.available_ports)

    def report_devices(self):
        devices = {key: list(value.keys()) for key, value in self.device_types.items()}
        signals_engine.answer_devices.emit(devices)

    def connect_device(self, device_type, device, port):
        try:
            self.devices[device_type] = self.device_types[device_type][device](port=port)
            time.sleep(1)
            if device_type == 'Mass Flow Controller':
                self.get_flow_set()
            for signal, function in self.device_functions[device_type].items():
                signal.connect(function)
        except SerialException:
            signals_engine.con_error.emit()

    def disconnect_device(self, device_type):
        for signal, function in self.device_functions[device_type].items():
            signal.disconnect(function)
        self.devices[device_type].close()
        self.devices[device_type] = None

    def get_flow_is(self):
        for channel in range(1, 5):
            worker = Worker(self.devices['Mass Flow Controller'].read_is_flow, channel)
            worker.signals.over.connect(lambda flow, chan: signals_engine.flow_is.emit(chan[0], flow))
            self.pool.start(worker)

    def get_flow_set(self):
        for channel in range(1, 5):
            worker = Worker(self.devices['Mass Flow Controller'].read_set_flow, channel)
            worker.signals.over.connect(lambda flow, chan: signals_engine.flow_set.emit(chan[0], flow))
            self.pool.start(worker)

    def set_flow(self, channel, flow):
        worker = Worker(self.devices['Mass Flow Controller'].set_flow, channel=channel, flow=flow)
        self.pool.start(worker)

    def get_valve_state(self):
        for channel in range(1, 5):
            worker = Worker(self.devices['Valve Controller'].read_valve_state, channel)
            worker.signals.over.connect(lambda state, chan: signals_engine.valve_state.emit(chan[0], state))
            self.pool.start(worker)

    def set_valve_state(self, channel, state):
        worker = Worker(self.devices['Valve Controller'].switch_valve, channel=channel, state=state)
        self.pool.start(worker)

    def get_pressure(self):
        runtime = (datetime.datetime.now() - self.log_start_time).seconds if self.log_start_time else None
        for channel in range(1, 1 + self.devices['Pressure Sensor'].channels):
            worker = Worker(self.devices['Pressure Sensor'].read_pressure, channel)
            worker.signals.over.connect(lambda pressure, chan: signals_engine.pressure.emit(chan[0], pressure, runtime))

            if self.is_logging:
                worker.signals.over.connect(lambda pressure, chan: self.add_log_data_point(chan[0], pressure))
            self.pool.start(worker)

    def start_logging(self):
        self.is_logging = True
        self.log_start_time = datetime.datetime.now() if not self.log_start_time else self.log_start_time

    def clear_log(self):
        self.is_logging = False
        self.log_start_time = None
        self.pressure_data = {channel: [] for channel in range(1, 4)}

    def export_log(self, filepath):
        """
        Tedious data aligning: The timestamps of separate channels (runtime -> pressure) are rounded to whole seconds
        and transfered into one dict (runtime -> 3 pressures), to align the 3 data series. This dict is then used to
        generate a csv file.
        """

        def _work():
            sorted_data = {}
            for channel, data in self.pressure_data.items():
                for runtime, pressure in data:
                    timestamp = int(runtime.timestamp())
                    if timestamp not in sorted_data.keys():
                        sorted_data[timestamp] = {channel: pressure}
                    else:
                        sorted_data[timestamp].update({channel: pressure})

            with open(filepath, 'w+') as file:
                file.write('UTC, Unix timestamp (s)' + ft.reduce(lambda x, y: x + y,
                                                                 [f', Pressure Channel {channel + 1}' for channel in
                                                                  range(self.devices[
                                                                            'Pressure Sensor'].channels)]) + '\n')
                for timestamp, datapoint in sorted_data.items():
                    timestring = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
                    # Godawful, I hate this
                    file.write(f'{timestring}, {timestamp}' +
                               ft.reduce(lambda x, y: x + y, [
                                   f', {datapoint.get(channel, math.nan) if datapoint.get(channel, math.nan) else math.nan :.3e}'
                                   for channel in datapoint.keys()]) + '\n')

        worker = Worker(_work)
        self.pool.start(worker)

    def add_log_data_point(self, channel, pressure):
        self.pressure_data[channel].append((datetime.datetime.now(), pressure))
