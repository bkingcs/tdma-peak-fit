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
from htdma_code.view.dma_1_dock_form import DMA_1_Form

from htdma_code.view.helper_widgets import TitleHLine
from htdma_code.view.dma_1_graph import DMA_1_Graph_Widget
from htdma_code.view.scan_data_graph import Scan_Data_Graph_Widget
from htdma_code.view.scan_dock_form import Scan_Form


class MainWindow(QMainWindow):
    def __init__(self, model: model_pkg.Model):
        super().__init__()

        self.model = model

        self.setWindowTitle("HTDMA ")
        self.resize(1200,800)

        # Set up the statusbar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready")

        # Set up the menu for the application
        self.create_menu()

        # Create all of the graph widgets
        self.create_view_graphs()

        # Set up the dock widget. Then, create the tabs that will be placed in the dock
        dockWidget = QDockWidget("", self)
        self.tabs = self.create_tab_widget_for_docker()
        dockWidget.setWidget(self.tabs)
        dockWidget.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea,dockWidget)

        # Finally, set up the main view itself
        self.setCentralWidget(self.create_center_widget())

    def create_view_graphs(self):
        self.dma_1_graph_widget = DMA_1_Graph_Widget()
        self.dma_1_graph_widget.set_model(self.model)

        self.scan_data_graph_widget = Scan_Data_Graph_Widget()
        self.scan_data_graph_widget.set_model(self.model)

    def create_tab_widget_for_docker(self):

        # Initialize tab screen
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.West)
        tab1 = QWidget()
        tab2 = QWidget()
        # self.tabs.resize(300, 200)

        # Add tabs
        tabs.addTab(tab1, "DMA 1 - Static")
        tabs.addTab(tab2, "DMA 2 - Scanning")

        # Create first tab
        self.dma_1_form = DMA_1_Form(parent=self,model=self.model)
        self.scan_form = Scan_Form(parent=self,model=self.model)
        tab1.setLayout(self.dma_1_form)
        tab2.setLayout(self.scan_form)

        return tabs

    def create_center_widget(self):

        splitter1 = Qw.QSplitter(Qt.Vertical)
        splitter1.addWidget(self.dma_1_graph_widget)
        splitter1.addWidget(self.scan_data_graph_widget)

        layout = Qw.QVBoxLayout()
        layout.addWidget(splitter1)

        # THe Qt way - a layout always needs a dummy widget
        frame = Qw.QFrame()
        frame.setLayout(layout)

        return frame

    def create_menu(self):
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("&File")
        self.file_open_action = QAction("&Open...",self)
        self.file_menu.addAction(self.file_open_action)

        self.help_menu = self.menu.addMenu("&Help")
        self.help_menu_action = QAction("Help",self)
        self.help_menu.addAction(self.help_menu_action)

    def update_dma1_widget_views_from_model(self):
        """
        Update all widgets related to dma1 based on whatever values the model contains
        """
        super().update()

        self.dma_1_form.update_from_model()
        self.dma_1_graph_widget.update_plot()

    def update_scan_widget_views_from_model(self):
        """
        Update all widgets related to a single scan based on whatever values the model contains
        """

        super().update()
        self.scan_form.update_from_model()
        self.scan_data_graph_widget.update_plot()


