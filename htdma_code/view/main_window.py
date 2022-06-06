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
from htdma_code.model.scan import MAX_PEAKS_TO_FIT

from htdma_code.view.helper_widgets import TitleHLine
from htdma_code.view.dma_1_graph import DMA_1_Graph_Widget
from htdma_code.view.scan_data_graph import Scan_Data_Graph_Widget

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

        # Create ALL of the fields that will be managed by this view and connected
        # to the model
        self.create_view_fields()

        # Now, create all of the extraneous controls. These are things like sliders and stuff
        # that are are connected to one of the primary fields
        self.create_view_controls()

        # Create all of the graph widgets
        self.create_view_graphs()

        # Set up the dock widget. Then, create the tabs that will be placed in the dock
        dockWidget = QDockWidget("Setup Info", self)
        self.tabs = self.create_tab_widget_for_docker()
        dockWidget.setWidget(self.tabs)
        dockWidget.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea,dockWidget)

        # Finally, set up the main view itself
        self.setCentralWidget(self.create_center_widget())

    def create_view_fields(self):
        """
        This is a pretty important function. It creates the primary widgets that will be connected
        to the model.
        """
        self.run_name_lineedit = QLineEdit()
        self.run_name_lineedit.setText("HTDMA test")
        self.run_name_lineedit.setEnabled(False)

        self.q_sh_lineedit = QLineEdit()
        self.q_sh_lineedit.setText("0.0")

        self.q_aIn_lineedit = QLineEdit()
        self.q_aIn_lineedit.setText("0.0")

        self.q_aOut_lineedit = QLineEdit()
        self.q_aOut_lineedit.setText("0.0")

        self.q_excess_lineedit = QLineEdit()
        self.q_excess_lineedit.setText("0.0")

        self.voltage_lineedit = QLineEdit()
        self.voltage_lineedit.setText("0")

        self.dp_center_label = QLabel("0")
        self.dp_range_label = QLabel("[ 0 - 0 ]")
        self.dp_spread_label = QLabel("0")

        self.scan_num_lineedit = QLineEdit()
        self.scan_num_lineedit.setText("0")

        self.scan_timestamp_label = QLabel("00:00:00")

        self.scan_up_time_label = QLabel()
        self.scan_down_time_label = QLabel()
        self.low_V_label = QLabel()
        self.high_V_label = QLabel()

        self.scan_fit_num_peaks_spinbox = Qw.QSpinBox()
        self.scan_fit_num_peaks_spinbox.setRange(1,MAX_PEAKS_TO_FIT)

    def create_view_controls(self):
        """
        This sets up controls used by the user to navigate settings
        and work through scans
        """
        self.voltage_slider = QSlider(Qt.Horizontal)
        self.voltage_slider.setMinimum(0)
        self.voltage_slider.setMaximum(10000)
        self.voltage_slider.setValue(0)
        self.voltage_slider.setTickPosition(QSlider.TicksBelow)
        self.voltage_slider.setTickInterval(2500)

        # Create the buttons to step through scans
        self.next_scan_button = Qw.QPushButton("Next")
        self.prev_scan_button = Qw.QPushButton("Prev")

        # Curve fitting button
        self.peak_fit_button = Qw.QPushButton("Fit Peaks")

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
        tabs.addTab(tab1, "DMA 1")
        tabs.addTab(tab2, "Scan")

        # Create first tab
        tab1.setLayout(self.create_dma_1_dock_tab_layout())
        tab2.setLayout(self.create_scan_dock_tab_layout())

        return tabs

    def create_dma_1_dock_tab_layout(self) -> QFormLayout:
        """
        Create the layout that will show dma 1
        """

        # We'll use a form layout container for the docker
        form = QFormLayout(self)

        # Start adding info
        form.addRow("Name", self.run_name_lineedit)

        form.addRow(TitleHLine("Flow settings"))
        form.addRow("Sheath Flow", self.q_sh_lineedit)
        form.addRow("Aerosol In", self.q_aIn_lineedit)
        form.addRow("Aerosol Out", self.q_aOut_lineedit)
        form.addRow("Excess Out", self.q_excess_lineedit)

        form.addRow(QLabel(""))
        form.addRow(TitleHLine("Voltage"))

        form.addRow("Voltage", self.voltage_lineedit)

        form.addRow(self.voltage_slider)

        form.addRow(QLabel(""))
        form.addRow(TitleHLine("Theoretical dP Distribution"))
        form.addRow("dP (nm)", self.dp_center_label)
        form.addRow("dP range", self.dp_range_label)
        form.addRow("dp spread", self.dp_spread_label)

        return form

    def create_scan_dock_tab_layout(self) -> QFormLayout:
        # We'll use a form layout container for the docker
        form = QFormLayout(self)

        # Start adding info
        form.addRow("Name", self.run_name_lineedit)

        form.addRow(QLabel(""))
        form.addRow(TitleHLine("Run Information"))

        form.addRow(QLabel(""))
        form.addRow(TitleHLine("Scan Details"))
        form.addRow("Scan #", self.scan_num_lineedit)
        form.addRow("Time", self.scan_timestamp_label)
        form.addRow("Low Voltage",self.low_V_label)
        form.addRow("High Voltage", self.high_V_label)
        form.addRow("Scan Up Time", self.scan_up_time_label)
        form.addRow("Scan Down Time", self.scan_down_time_label)

        form.addRow(QLabel(""))
        hbox = Qw.QHBoxLayout()
        hbox.addWidget(self.prev_scan_button)
        hbox.addWidget(self.next_scan_button)
        form.addRow(hbox)

        form.addRow(QLabel(""))
        form.addRow(TitleHLine("Peak Fitting"))
        form.addRow("Number of peaks to fit", self.scan_fit_num_peaks_spinbox)
        form.addRow(self.peak_fit_button)

        return form

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
        self.q_sh_lineedit.setText("{:.1f}".format(self.model.dma1.q_sh_lpm))
        self.q_aIn_lineedit.setText("{:.1f}".format(self.model.dma1.q_aIn_lpm))
        self.q_aOut_lineedit.setText("{:.1f}".format(self.model.dma1.q_aOut_lpm))
        self.q_excess_lineedit.setText("{:1f}".format(self.model.dma1.q_excess_lpm))
        self.voltage_lineedit.setText("{:.0f}".format(self.model.dma1.voltage))
        self.voltage_slider.setValue(self.model.dma1.voltage)

        self.dp_center_label.setText("{:.1f}".format(self.model.dma1.dp_center))
        self.dp_range_label.setText("[ {:.1f} - {:.1f} ]".format(self.model.dma1.dp_left_bottom,self.model.dma1.dp_right_bottom))
        self.dp_spread_label.setText("{:.1f}".format(self.model.dma1.dp_right_bottom - self.model.dma1.dp_left_bottom))

        self.dma_1_graph_widget.update_plot()

    def update_scan_widget_views_from_model(self):
        """
        Update all widgets related to a single scan based on whatever values the model contains
        """
        print("update_scan_widget_views: " + repr(self.model.current_scan))
        if self.model.current_scan is not None:
            self.scan_num_lineedit.setText(str(self.model.current_scan.scan_id_from_data))
            self.scan_timestamp_label.setText(self.model.current_scan.time_stamp.strftime("%H:%M:%S"))
            self.low_V_label.setText("{:.0f}".format(self.model.current_scan.low_V))
            self.high_V_label.setText("{:.0f}".format(self.model.current_scan.high_V))
            self.scan_up_time_label.setText("{:.0f}".format(self.model.current_scan.scan_up_time))
            self.scan_down_time_label.setText("{:.0f}".format(self.model.current_scan.scan_down_time))
        else:
            self.scan_num_lineedit.setText("")
            self.scan_timestamp_label.setText("00:00:00")
            self.low_V_label.setText("0")
            self.high_V_label.setText("0")
            self.scan_up_time_label.setText("")
            self.scan_down_time_label.setText("")

        self.scan_data_graph_widget.update_plot()


