import functools as ft
import datetime
import math

import pubsub.pub
import serial.tools.list_ports
from PySide2.QtCore import QThreadPool
from pubsub.pub import sendMessage
from serial import SerialException

from src.Drivers.ElchWorks import Ventolino, Valvolino
from src.Drivers.Aera import ROD4
from src.Drivers.Leybold import CenterOne
from src.Engine.ThreadDecorators import Worker
from src.Drivers.TestDevices import *

# TODO: Implement some notification system for serial failures

TEST_MODE = False


class MassflowControlEngine:
    def __init__(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}

        self.device_types = {'Mass Flow Controller': {'Ventolino': Ventolino, 'Area ROD-4': ROD4},
                             'Valve Controller': {'Valvolino': Valvolino},
                             'Pressure Sensor': {'Center One': CenterOne}}
        if TEST_MODE:
            self.available_ports.update({'COM Test': 'Test Port'})
            self.device_types['Mass Flow Controller'].update({'Test MFC': TestMFC})
            self.device_types['Valve Controller'].update({'Test Valve Controller': TestValveController})
            self.device_types['Pressure Sensor'].update({'Test Pressure Sensor': TestPressureSensor})

        self.device_functions = {'Mass Flow Controller':
                                     {'gui.get.flow_is': self.get_flow_is,
                                      'gui.get.flow_set': self.get_flow_set,
                                      'gui.set.flow': self.set_flow},
                                 'Valve Controller':
                                     {'gui.get.valve_state': self.get_valve_state,
                                      'gui.set.valve_state': self.set_valve_state},
                                 'Pressure Sensor':
                                     {'gui.get.pressure': self.get_pressure}}

        self.devices = {key: None for key in self.device_types}

        self.is_logging = False
        self.log_start_time = None
        self.pressure_data = {channel: [] for channel in range(1, 4)}

        pubsub.pub.subscribe(self.refresh_available_ports, 'gui.con.get_ports')
        pubsub.pub.subscribe(self.report_devices, 'gui.con.get_devices')
        pubsub.pub.subscribe(self.connect_device, 'gui.con.connect_device')
        pubsub.pub.subscribe(self.disconnect_device, 'gui.con.disconnect_device')

        pubsub.pub.subscribe(self.start_logging, 'gui.plot.start')
        pubsub.pub.subscribe(self.clear_log, 'gui.plot.clear')
        pubsub.pub.subscribe(self.export_log, 'gui.plot.export')

        self.pool = QThreadPool()

    def refresh_available_ports(self):
        self.available_ports = {port[0]: port[1] for port in serial.tools.list_ports.comports()}
        if TEST_MODE:
            self.available_ports['COM Test'] = 'Test Port'
        pubsub.pub.sendMessage(topicName='engine.answer.ports', ports=self.available_ports)

    def report_devices(self):
        devices = {key: list(value.keys()) for key, value in self.device_types.items()}
        pubsub.pub.sendMessage(topicName='engine.answer.devices', devices=devices)

    def connect_device(self, device_type, device, port):
        try:
            self.devices[device_type] = self.device_types[device_type][device](port=port)
            time.sleep(1)
            if device_type == 'Mass Flow Controller':
                self.get_flow_set()
            for topic, function in self.device_functions[device_type].items():
                pubsub.pub.subscribe(function, topic)
        except SerialException:
            sendMessage(topicName='engine.error.connection', text='Serial connection error!')

    def disconnect_device(self, device_type):
        for topic, function in self.device_functions[device_type].items():
            pubsub.pub.unsubscribe(function, topic)
        self.devices[device_type].close()
        self.devices[device_type] = None

    def get_flow_is(self):
        for channel in range(1, 5):
            worker = Worker(ft.partial(self.devices['Mass Flow Controller'].read_is_flow, channel))
            worker.signals.over.connect(lambda flow, chan=channel:
                                        sendMessage('engine.answer.flow_is', flow=flow, channel=chan))
            self.pool.start(worker)

    def get_flow_set(self):
        for channel in range(1, 5):
            worker = Worker(ft.partial(self.devices['Mass Flow Controller'].read_set_flow, channel))
            worker.signals.over.connect(lambda flow, chan=channel:
                                        sendMessage('engine.answer.flow_set', flow=flow, channel=chan))
            self.pool.start(worker)

    def set_flow(self, channel, flow):
        worker = Worker(ft.partial(self.devices['Mass Flow Controller'].set_flow, channel=channel, flow=flow))
        self.pool.start(worker)

    def get_valve_state(self):
        for channel in range(1, 5):
            worker = Worker(ft.partial(self.devices['Valve Controller'].read_valve_state, channel))
            worker.signals.over.connect(lambda state, chan=channel:
                                        sendMessage('engine.answer.valve_state', state=state, channel=chan))
            self.pool.start(worker)

    def set_valve_state(self, channel, state):
        worker = Worker(ft.partial(self.devices['Valve Controller'].switch_valve, channel=channel, state=state))
        self.pool.start(worker)

    def get_pressure(self):
        runtime = (datetime.datetime.now() - self.log_start_time).seconds if self.log_start_time else None
        for channel in range(1, 1 + self.devices['Pressure Sensor'].channels):
            worker = Worker(ft.partial(self.devices['Pressure Sensor'].read_pressure, channel))
            worker.signals.over.connect(lambda pressure, chan=channel: sendMessage('engine.answer.pressure',
                                                                                   channel=chan, pressure=pressure,
                                                                                   runtime=runtime))
            if self.is_logging:
                worker.signals.over.connect(lambda pressure, chan=channel:
                                            self.add_log_data_point(channel=chan, pressure=pressure))
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
                    file.write(f'{timestring}, {timestamp}' +
                               ft.reduce(lambda x, y: x + y, [f', {datapoint.get(channel, math.nan):.3e}'
                                                              for channel in datapoint.keys()]) + '\n')

        worker = Worker(_work)
        self.pool.start(worker)

    def add_log_data_point(self, channel, pressure):
        self.pressure_data[channel].append((datetime.datetime.now(), pressure))
