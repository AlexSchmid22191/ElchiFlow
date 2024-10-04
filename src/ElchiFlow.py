from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.Engine.Engine import MassflowControlEngine
from src.QtInterface.ElchMainWindow import ElchMainWindow


def main():
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = MassflowControlEngine()
    gui = ElchMainWindow()
    app.exec()


if __name__ == '__main__':
    main()
