import functools

import pubsub.pub
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QDoubleSpinBox, QLabel, QButtonGroup, QCheckBox, \
    QHBoxLayout, QGridLayout


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
            valve_grid.addWidget(valve, (key - 1) // 2, (key - 1) % 2)
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
