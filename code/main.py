import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton

import sys
from PySide2.QtWidgets import QApplication

from code.controller.controller import Controller
from code.model.model import Model
from code.view.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Instantiate a model
    model = Model()

    # Instantiate the main window to represent the view
    window = MainWindow(model)

    # Instantiate a controller to connect both
    controller = Controller(model,window)

    # Bring up the window
    window.show()

    sys.exit(app.exec_())