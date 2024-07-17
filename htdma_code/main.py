"""
MIT License

Copyright (c) 2023-24 Brian R. King

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton

import sys
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication

from htdma_code.controller.controller import Controller
from htdma_code.model.model import Model
from htdma_code.view.main_window import MainWindow

# Main version number for the software
SW_VERSION="202407216.01"

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