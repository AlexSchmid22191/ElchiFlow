import pubsub.pub
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QComboBox, \
    QButtonGroup


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
