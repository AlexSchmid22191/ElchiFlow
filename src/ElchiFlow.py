from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from src.Engine import topic_def
from src.Engine.Engine import MassflowControlEngine
from src.QtInterface.ElchMainWindow import ElchMainWindow
from pubsub.pub import addTopicDefnProvider, TOPIC_TREE_FROM_CLASS, setTopicUnspecifiedFatal


addTopicDefnProvider(topic_def, TOPIC_TREE_FROM_CLASS)
setTopicUnspecifiedFatal(True)


def main():
    app = QApplication()
    app.setWindowIcon(QIcon('Icons/Logo.ico'))
    engine = MassflowControlEngine()
    gui = ElchMainWindow()
    app.exec_()


if __name__ == '__main__':
    main()


# TODO: Lin /Log scale
# Autoscale
# Log modus
# Add sensor mode bla