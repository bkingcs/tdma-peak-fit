from PySide2.QtCore import Qt

from PySide2.QtWidgets import (
    QLabel,
    QMainWindow,
    QWidget,
    QStatusBar,
    QDockWidget,
    QFormLayout,
    QLineEdit, QTabWidget, QAction, QSlider
)

import PySide2.QtWidgets as Qw

#from layout_colorwidget import Color
import htdma_code.model.model as model_pkg
from htdma_code.view.dma_1_center_widget import DMA_1_Center_Frame
from htdma_code.view.dma_1_dock_form import DMA_1_Form
from htdma_code.view.results_center_widget import Total_Results_Center_Frame
from htdma_code.view.scan_dock_form import Scan_Form
from htdma_code.view.scan_center_widget import Scan_Data_Center_Frame

class MainWindow(QMainWindow):
    def __init__(self, model: model_pkg.Model, sw_version: str):
        super().__init__()

        self.model = model

        self.setWindowTitle("HTDMA ")
        self.resize(1200,800)

        # Set up the statusbar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Version: " + sw_version + " - Ready")

        # Set up the menu for the application
        self.create_menu()

        # Set up the dock widget. Then, create the tabs that will be placed in the dock
        self.docker_tabs = self.create_tab_widget_for_dock()
        self.docker_tabs.setCurrentIndex(0)

        dockWidget = QDockWidget("", self)
        dockWidget.setWidget(self.docker_tabs)
        dockWidget.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea,dockWidget)

        self.update_center_widget()

    def create_tab_widget_for_dock(self) -> QTabWidget:

        # Initialize tab screen
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tab1 = QWidget()
        tab2 = QWidget()
        tab3 = QWidget()
        # self.tabs.resize(300, 200)

        # Add tabs
        tabs.addTab(tab1, "DMA 1 - Static")
        tabs.addTab(tab2, "DMA 2 - Scanning")
        tabs.addTab(tab3, "Results")

        # Create first tab
        self.dma_1_form = DMA_1_Form(parent=self,model=self.model)
        self.scan_form = Scan_Form(parent=self,model=self.model)
        tab1.setLayout(self.dma_1_form)
        tab2.setLayout(self.scan_form)

        return tabs

    def create_menu(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.file_open_action = QAction("&Open...",self)
        self.file_menu.addAction(self.file_open_action)

        self.help_menu = self.menu.addMenu("&Help")
        self.help_menu_action = QAction("Help",self)
        self.help_menu.addAction(self.help_menu_action)

    def update_dock_form_from_model(self):
        super().update()
        if self.docker_tabs.currentIndex() == 0:
            self.dma_1_form.update_from_model()
        elif self.docker_tabs.currentIndex() == 1:
            self.scan_form.update_from_model()

    def update_center_from_model(self):
        super().update()
        self.centralWidget().update_from_model()

    def update_from_model(self):
        self.update_dock_form_from_model()
        self.update_center_from_model()

    def update_center_widget(self):
        if self.docker_tabs.currentIndex() == 0:
            self.dma_1_center = DMA_1_Center_Frame(parent=self, model=self.model)
            self.setCentralWidget(self.dma_1_center)
        elif self.docker_tabs.currentIndex() == 1:
            self.scan_data_center = Scan_Data_Center_Frame(parent=self, model=self.model)
            self.setCentralWidget(self.scan_data_center)
        elif self.docker_tabs.currentIndex() == 2:
            self.results_data_center = Total_Results_Center_Frame(parent=self,model=self.model)
            self.setCentralWidget(self.results_data_center)
