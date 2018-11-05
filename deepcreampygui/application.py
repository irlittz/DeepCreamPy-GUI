import sys

from PyQt5.Qt import QApplication

from deepcreampygui.views.mainwindow import MainWindow

APPLICATION_NAME = 'DeepCreamPy'


def start():
    application = QApplication(sys.argv)
    application.setApplicationName(APPLICATION_NAME)

    window = MainWindow()
    window.show()

    application.exec()
