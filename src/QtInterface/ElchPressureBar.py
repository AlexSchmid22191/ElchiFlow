import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from src.Signals import signals_gui, signals_engine


class ElchPressureBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        channels = range(1, 4)

        self.setAttribute(Qt.WA_StyledBackground, True)

        icons = {key: QLabel() for key in channels}
        labels = {key: QLabel(text=f'Channel {key}', objectName='label') for key in channels}
        self.values = {key: QLabel(text='- - -', objectName='value') for key in channels}
        vboxes = {key: QVBoxLayout() for key in channels}

        hbox = QHBoxLayout()
        for key in channels:
            vboxes[key].addWidget(self.values[key])
            vboxes[key].addWidget(labels[key])
            vboxes[key].setContentsMargins(0, 0, 0, 0)
            vboxes[key].setSpacing(5)
            hbox.addWidget(icons[key])
            hbox.addStretch(1)
            hbox.addLayout(vboxes[key])
            hbox.addStretch(10)
            icons[key].setPixmap(QPixmap('Icons/Ring_{:d}.png'.format(key)))
        hbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(hbox)

        self.timer = QTimer(parent=self)
        self.timer.timeout.connect(signals_gui.get_pressure.emit)
        self.timer.start(1000)

        signals_engine.pressure.connect(self.update_pressure)

    def update_pressure(self, channel, pressure, runtime):
        if pressure:
            self.values[channel].setText(f'{self.scientific_exponents(pressure)} mbar')

    @staticmethod
    def scientific_exponents(number):
        exponent = math.floor(math.log10(abs(number)))
        mantissa = number / 10 ** exponent
        return f'{mantissa:1.2f} \u00B7 10<sup>{exponent}</sup>'
