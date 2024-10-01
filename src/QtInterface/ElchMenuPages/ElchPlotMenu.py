import functools

import pubsub.pub
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QButtonGroup, QFileDialog, QCheckBox


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
