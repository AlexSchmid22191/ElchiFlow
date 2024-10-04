from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from src.Signals import signals_engine, signals_gui


class ElchStatusBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.channels = range(1, 5)

        labels = {channel: QLabel(text=f'Channel {channel}', objectName='label') for channel in self.channels}
        vboxes = {channel: QVBoxLayout() for channel in self.channels}
        self.icons = {channel: QLabel() for channel in self.channels}
        self.values = {channel: QLabel(text='- - -', objectName='value') for channel in self.channels}

        hbox = QHBoxLayout()
        for channel in self.channels:
            vboxes[channel].addWidget(self.values[channel])
            vboxes[channel].addWidget(labels[channel])
            vboxes[channel].setContentsMargins(0, 0, 0, 0)
            vboxes[channel].setSpacing(5)
            hbox.addWidget(self.icons[channel])
            hbox.addStretch(1)
            hbox.addLayout(vboxes[channel])
            hbox.addStretch(10)
            self.icons[channel].setPixmap(QPixmap('Icons/Valve.png'))
        hbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(hbox)

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(signals_gui.get_flow_is.emit)
        self.timer.timeout.connect(signals_gui.get_flow_set.emit)
        self.timer.timeout.connect(signals_gui.get_valve_state.emit)
        self.timer.start(1000)

        signals_engine.flow_is.connect(self.update_flow_is)
        signals_engine.flow_set.connect(self.update_flow_set)
        signals_engine.valve_state.connect(self.update_valve_state)

    def update_flow_is(self, channel, flow):
        assert channel in self.channels, f'Invalid channel: {channel}'
        self.values[channel].setText(f'{flow:.1f} %')

    def update_valve_state(self, channel, state):
        assert channel in self.channels, f'Invalid channel: {channel}'
        self.icons[channel].setPixmap(QPixmap('Icons/Valve_Glow.png') if state else QPixmap('Icons/Valve.png'))

    def update_flow_set(self, channel, flow):
        pass
