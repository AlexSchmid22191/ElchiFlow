import functools
import pubsub.pub
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDoubleSpinBox, QLabel, QRadioButton, QComboBox, \
    QFormLayout, QButtonGroup, QSpinBox, QFileDialog, QCheckBox, QHBoxLayout, QGridLayout


class ElchMenuPages(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFixedWidth(255)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.menus = {'Devices': ElchDeviceMenu(), 'Control': ElchControlMenu(), 'Plotting': ElchPlotMenu()}

        vbox = QVBoxLayout()
        for menu in self.menus:
            self.menus[menu].setVisible(False)
            vbox.addWidget(self.menus[menu])
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.setLayout(vbox)

    def adjust_visibility(self, button, visibility):
        menu = button.objectName()
        self.menus[menu].setVisible(visibility)


class ElchDeviceMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.labels = {key: QLabel(text=key, objectName='Header') for key in ['Mass Flow Controller',
                                                                              'Valve Controller', 'Pressure Sensor']}
        self.device_menus = {key: QComboBox() for key in self.labels}
        self.port_menus = {key: QComboBox() for key in self.labels}
        self.connect_buttons = {key: QPushButton(text='Connect', objectName=key) for key in self.labels}

        self.buttongroup = QButtonGroup()
        self.buttongroup.setExclusive(False)
        self.buttongroup.buttonToggled.connect(self.connect_device)

        self.refresh_button = QPushButton(text='Refresh Serial', objectName='Refresh')

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addSpacing(20)

        for key in self.labels:
            self.buttongroup.addButton(self.connect_buttons[key])
            self.connect_buttons[key].setCheckable(True)
            vbox.addWidget(self.labels[key])
            vbox.addWidget(self.device_menus[key])
            vbox.addWidget(self.port_menus[key])
            vbox.addWidget(self.connect_buttons[key])
            vbox.addSpacing(20)

        vbox.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(lambda: pubsub.pub.sendMessage('gui.con.get_ports'))
        vbox.addStretch()
        self.setLayout(vbox)

        pubsub.pub.subscribe(listener=self.update_ports, topicName='engine.answer.ports')
        pubsub.pub.subscribe(listener=self.update_devices, topicName='engine.answer.devices')

        pubsub.pub.sendMessage('gui.con.get_ports')
        pubsub.pub.sendMessage('gui.con.get_devices')

    def update_ports(self, ports):
        """Populate the controller and sensor menus with lists of device names and ports"""
        for key, menu in self.port_menus.items():
            menu.clear()
            menu.addItems(ports)
            for port, description in ports.items():
                index = menu.findText(port)
                menu.setItemData(index, description, Qt.ToolTipRole)

    def update_devices(self, devices):
        for key in self.device_menus:
            self.device_menus[key].clear()
            self.device_menus[key].addItems(devices[key])

    def connect_device(self, source, state):
        key = source.objectName()
        port = self.port_menus[key].currentText()
        device = self.device_menus[key].currentText()

        if state:
            pubsub.pub.sendMessage('gui.con.connect_device', device_type=key, device=device, port=port)
        else:
            pubsub.pub.sendMessage('gui.con.disconnect_device', device_type=key)


class ElchControlMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)

        vbox.addWidget(QLabel(text='Mass Flow', objectName='Header'))
        self.entries = {key: QDoubleSpinBox(decimals=1, singleStep=1, minimum=0, maximum=100, suffix=' %')
                        for key in range(1, 5)}
        for key, entry in self.entries.items():
            entry.setKeyboardTracking(False)
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(text=f'Channel {key}'))
            hbox.addWidget(entry)
            vbox.addLayout(hbox)
            entry.valueChanged.connect(functools.partial(self.set_flow, channel=key))

        vbox.addSpacing(10)

        vbox.addWidget(QLabel(text='Valves', objectName='Header'))
        self.valves = {key: QCheckBox(parent=self, text=f'Valve {key}', objectName=str(key)) for key in range(1, 5)}
        self.check_group = QButtonGroup()
        self.check_group.setExclusive(False)
        self.check_group.buttonToggled.connect(self.set_valve_state)
        valve_grid = QGridLayout()
        for key, valve in self.valves.items():
            valve.setChecked(False)
            self.check_group.addButton(valve)
            valve_grid.addWidget(valve, (key-1)//2, (key-1) % 2)
        vbox.addLayout(valve_grid)

        vbox.addSpacing(10)

        refresh_button = QPushButton(text='Refresh', objectName='Refresh')
        refresh_button.clicked.connect(lambda: pubsub.pub.sendMessage('gui.get.valve_state'))
        refresh_button.clicked.connect(lambda: pubsub.pub.sendMessage('gui.get.flow_set'))
        vbox.addWidget(refresh_button)

        vbox.addStretch()
        self.setLayout(vbox)

        pubsub.pub.subscribe(self.update_valve_state, 'engine.answer.valve_state')
        pubsub.pub.subscribe(self.update_set_flow, 'engine.answer.flow_set')

    @staticmethod
    def set_flow(flow, channel):
        pubsub.pub.sendMessage('gui.set.flow', channel=channel, flow=flow)

    @staticmethod
    def set_valve_state(source, state):
        pubsub.pub.sendMessage('gui.set.valve_state', channel=int(source.objectName()), state=state)

    def update_valve_state(self, channel, state):
        assert 1 <= channel <= 4, f'Invalid channel: {channel}'
        self.check_group.blockSignals(True)
        self.valves[channel].setChecked(state)
        self.check_group.blockSignals(False)

    def update_set_flow(self, channel, flow):
        assert 1 <= channel <= 4, f'Invalid channel: {channel}'
        self.entries[channel].blockSignals(True)
        self.entries[channel].setValue(flow)
        self.entries[channel].blockSignals(False)


class ElchPlotMenu(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        controls = ['Start', 'Clear', 'Export', 'Scale']
        self.buttons = {key: QPushButton(parent=self, text=key, objectName=key) for key in controls}
        self.buttons['Start'].setCheckable(True)
        self.buttons['Scale'].setCheckable(True)
        self.checks = {key: QCheckBox(parent=self, text=f'Channel {key}', objectName=str(key)) for key in range(1, 4)}
        self.check_group = QButtonGroup()
        self.check_group.setExclusive(False)

        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(text='Plotting', objectName='Header'))
        for key in controls:
            vbox.addWidget(self.buttons[key])
            self.buttons[key].clicked.connect({'Start': functools.partial(self.start_stop_plotting),
                                               'Clear': self.clear_pplot, 'Export': self.export_data}.get(key, None))
        vbox.addSpacing(20)
        vbox.addWidget(QLabel(text='Data sources', objectName='Header'))
        for key, button in self.checks.items():
            button.setChecked(True)
            self.check_group.addButton(button)
            vbox.addWidget(button)
        vbox.addStretch()
        vbox.setSpacing(10)
        vbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(vbox)

    def start_stop_plotting(self):
        pubsub.pub.sendMessage('gui.plot.start' if self.buttons['Start'].isChecked() else 'gui.plot.stop')

    def clear_pplot(self):
        pubsub.pub.sendMessage('gui.plot.clear')
        if self.buttons['Start'].isChecked():
            self.buttons['Start'].click()

    def export_data(self):
        if (file_path := QFileDialog.getSaveFileName(self, 'Save as...', 'Logs/Log.csv', 'CSV (*.csv)')[0]) != '':
            pubsub.pub.sendMessage('gui.plot.export', filepath=file_path)
