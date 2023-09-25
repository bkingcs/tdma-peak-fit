import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton

import sys
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication

from htdma_code.controller.controller import Controller
from htdma_code.model.model import Model
from htdma_code.view.main_window import MainWindow

# Main version number for the software
SW_VERSION="20230925.01"

if __name__ == '__main__':

    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # Instantiate a model
    model = Model()

    # Instantiate the main window to represent the view
    window = MainWindow(model,SW_VERSION)

    # Instantiate a controller to connect both
    controller = Controller(model,window)

    # Bring up the window
    window.show()

    sys.exit(app.exec_())