from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QToolButton, QDialog, QLabel, QPushButton, QVBoxLayout
from PySide6.QtGui import QPixmap


class ElchTitlebar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setMinimumHeight(50)
        buttons = {key: QToolButton(self, objectName=key) for key in ['About', 'Minimize', 'Close']}

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
        buttons['About'].clicked.connect(self.show_about)

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

    def show_about(self):
        dlg = QDialog(self)
        dlg.setWindowTitle('About')
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(20, 20, 20, 20)
        vbox.setSpacing(10)
        vbox.addWidget(QLabel('ElchiFlow 2.0', objectName='Header'), alignment=Qt.AlignHCenter)
        vbox.addWidget(QLabel('License: CC-BY-SA 4.0'), alignment=Qt.AlignHCenter)

        icon = QLabel()
        icon.setPixmap(QPixmap('Icons/cc-by-sa.png').scaled(150, 141 * 150 / 403))
        icon.setFixedSize(150, 141 * 150 / 403)
        vbox.addWidget(icon, alignment=Qt.AlignHCenter)

        vbox.addWidget(QLabel('Maintainer: Alex Schmid'), alignment=Qt.AlignHCenter)
        vbox.addWidget(QLabel('Contact: alex.schmid91@gmail.com'), alignment=Qt.AlignHCenter)

        source_label = QLabel()
        source_label.setText('Source: https://github.com/AlexSchmid22191/ElchiFlow')
        source_label.setOpenExternalLinks(True)
        vbox.addWidget(source_label, alignment=Qt.AlignHCenter)
        vbox.addWidget(button := QPushButton('Close'))
        button.clicked.connect(dlg.close)

        dlg.setLayout(vbox)
        dlg.exec()
