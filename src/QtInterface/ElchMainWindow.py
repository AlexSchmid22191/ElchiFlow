from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSizeGrip

from src.QtInterface.ElchMenu import ElchMenu
from src.QtInterface.ElchPlot import ElchPlot
from src.QtInterface.ElchPressureBar import ElchPressureBar
from src.QtInterface.ElchRibbon import ElchRibbon
from src.QtInterface.ElchStatusBar import ElchStatusBar
from src.QtInterface.ElchTitleBar import ElchTitlebar


class ElchMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowFlags(Qt.FramelessWindowHint)

        QFontDatabase.addApplicationFont('Fonts/Roboto-Light.ttf')
        QFontDatabase.addApplicationFont('Fonts/Roboto-Regular.ttf')

        with open('QtInterface/style.qss') as stylefile:
            self.setStyleSheet(stylefile.read())

        self.controlmenu = ElchMenu()
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
