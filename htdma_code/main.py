import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton

import sys
from PySide2.QtWidgets import QApplication

from htdma_code.controller.controller import Controller
from htdma_code.model.model import Model
from htdma_code.view.main_window import MainWindow

# Main version number for the software
SW_VERSION="20221021.01"

if __name__ == '__main__':
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