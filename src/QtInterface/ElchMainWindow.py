import math
import pubsub.pub
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QPixmap, QFontDatabase
from PySide2.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QButtonGroup, \
    QLabel, QToolButton, QSizeGrip

from src.QtInterface.ElchMenuPages import ElchMenuPages
from src.QtInterface.ElchPlot import ElchPlot


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint)

        QFontDatabase.addApplicationFont('Fonts/Roboto-Light.ttf')
        QFontDatabase.addApplicationFont('Fonts/Roboto-Regular.ttf')

        with open('QtInterface/style.qss') as stylefile:
            self.setStyleSheet(stylefile.read())

        self.controlmenu = ElchMenuPages()
        self.ribbon = ElchRibbon(menus=self.controlmenu.menus)
        self.matplotframe = ElchPlot()
        self.titlebar = ElchTitlebar()
        self.statusbar = ElchStatusBar()
        self.flowbar = ElchPressureBar()

        panel_spacing = 20

        vbox_innnerest = QVBoxLayout()
        vbox_innnerest.addWidget(self.matplotframe, stretch=1)
        vbox_innnerest.addWidget(self.flowbar, stretch=0)
        vbox_innnerest.setSpacing(panel_spacing)
        vbox_innnerest.setContentsMargins(0, 0, 0, 0)

        hbox_inner = QHBoxLayout()
        hbox_inner.addLayout(vbox_innnerest, stretch=1)
        hbox_inner.addWidget(self.controlmenu, stretch=0)
        hbox_inner.setSpacing(panel_spacing)
        hbox_inner.setContentsMargins(0, 0, 0, 0)

        vbox_inner = QVBoxLayout()
        vbox_inner.addWidget(self.statusbar, stretch=0)
        vbox_inner.addLayout(hbox_inner, stretch=1)
        vbox_inner.setSpacing(panel_spacing)
        vbox_inner.setContentsMargins(panel_spacing, panel_spacing, panel_spacing - 13, panel_spacing)

        sizegrip = QSizeGrip(self)
        hbox_mid = QHBoxLayout()
        hbox_mid.addLayout(vbox_inner, stretch=1)
        hbox_mid.addWidget(sizegrip, alignment=Qt.AlignBottom | Qt.AlignRight)
        hbox_mid.setContentsMargins(0, 0, 0, 0)
        hbox_mid.setSpacing(0)

        vbox_outer = QVBoxLayout()
        vbox_outer.addWidget(self.titlebar, stretch=0)
        vbox_outer.addLayout(hbox_mid, stretch=1)
        vbox_outer.setContentsMargins(0, 0, 0, 0)
        vbox_outer.setSpacing(0)

        hbox_outer = QHBoxLayout()
        hbox_outer.addWidget(self.ribbon, stretch=0)
        hbox_outer.addLayout(vbox_outer, stretch=1)
        hbox_outer.setContentsMargins(0, 0, 0, 0)
        hbox_outer.setSpacing(0)

        self.ribbon.buttongroup.buttonToggled.connect(self.controlmenu.adjust_visibility)
        self.ribbon.menu_buttons['Devices'].setChecked(True)

        self.controlmenu.menus['Plotting'].buttons['Start'].clicked.connect(self.matplotframe.start_plotting)
        self.controlmenu.menus['Plotting'].buttons['Clear'].clicked.connect(self.matplotframe.clear_plot)
        self.controlmenu.menus['Plotting'].buttons['Scale'].clicked.connect(self.matplotframe.switch_scale)

        self.controlmenu.menus['Plotting'].check_group.buttonToggled.connect(self.matplotframe.set_plot_visibility)

        self.setLayout(hbox_outer)
        self.show()


class ElchTitlebar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(50)
        buttons = {key: QToolButton(self, objectName=key) for key in ['Minimize', 'Close']}

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addStretch(10)
        for key in buttons:
            buttons[key].setFixedSize(50, 50)
            hbox.addWidget(buttons[key])

        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        self.setLayout(hbox)

        self.dragPosition = None
        buttons['Minimize'].clicked.connect(self.minimize)
        buttons['Close'].clicked.connect(self.close)

    def mouseMoveEvent(self, event):
        # Enable mouse dragging
        if event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.dragPosition)
            event.accept()

    def mousePressEvent(self, event):
        # Enable mouse dragging
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.parent().frameGeometry().topLeft()
            event.accept()

    def minimize(self):
        self.parent().showMinimized()

    def close(self):
        self.parent().close()


class ElchRibbon(QWidget):
    def __init__(self, menus=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.menus = menus if menus is not None else ['Devices', 'Control', 'Setpoints', 'PID', 'Plotting', 'Logging']
        self.menu_buttons = {key: QPushButton(parent=self, objectName=key) for key in self.menus}
        self.buttongroup = QButtonGroup()
        elchicon = QLabel()
        elchicon.setPixmap(QPixmap('Icons/ElchiHead.png'))

        vbox = QVBoxLayout()
        vbox.addWidget(elchicon, alignment=Qt.AlignHCenter)
        for key in self.menus:
            vbox.addWidget(self.menu_buttons[key])
            self.buttongroup.addButton(self.menu_buttons[key])
            self.menu_buttons[key].setCheckable(True)
            self.menu_buttons[key].setFixedSize(150, 100)

        vbox.addStretch()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setMinimumWidth(150)
        self.setLayout(vbox)


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
        self.timer.timeout.connect(lambda: pubsub.pub.sendMessage(topicName='gui.get.flow_is'))
        self.timer.timeout.connect(lambda: pubsub.pub.sendMessage(topicName='gui.get.valve_state'))
        self.timer.start(1000)
        pubsub.pub.subscribe(self.update_flow, topicName='engine.answer.flow_is')
        pubsub.pub.subscribe(self.update_valve_state, topicName='engine.answer.valve_state')

    def update_flow(self, channel, flow):
        assert channel in self.channels, f'Invalid channel: {channel}'
        self.values[channel].setText(f'{flow:.1f} %')

    def update_valve_state(self, channel, state):
        assert channel in self.channels, f'Invalid channel: {channel}'
        self.icons[channel].setPixmap(QPixmap('Icons/Valve_Glow.png') if state else QPixmap('Icons/Valve.png'))


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
        self.timer.timeout.connect(lambda: pubsub.pub.sendMessage(topicName='gui.get.pressure'))
        pubsub.pub.subscribe(self.update_pressure, topicName='engine.answer.pressure')
        self.timer.start(1000)

    def update_pressure(self, channel, pressure, runtime):
        if pressure:
            self.values[channel].setText(f'{self.scientific_exponents(pressure)} mbar')

    @staticmethod
    def scientific_exponents(number):
        exponent = math.floor(math.log10(abs(number)))
        mantissa = number / 10**exponent
        return f'{mantissa:1.2f} \u00B7 10<sup>{exponent}</sup>'


