from PySide2.QtCore import Qt
import PySide2.QtWidgets as Qw
from PySide2.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QSlider
)

from htdma_code.view.helper_widgets import TitleHLine
import htdma_code.model.model as model_pkg
from htdma_code.model.scan import MAX_PEAKS_TO_FIT

class Scan_Form(QFormLayout):
    """
    This is the container for showing the scan tab
    """

    def __init__(self, parent, model: model_pkg.Model):
        super().__init__(parent)

        self.model = model
        self._create_form_widgets()
        self._add_widgets_to_form()

    def _create_form_widgets(self):
        self.dma_2_name_label = QLabel()
        self.dma_2_name_label.setText("-- not loaded --")
        self.dma_2_name_label.setStyleSheet("border: 1px solid black")

        self.scan_num_lineedit = QLineEdit()
        self.scan_num_lineedit.setText("0")

        self.scan_timestamp_label = QLabel("00:00:00")

        self.scan_up_time_label = QLabel()
        self.scan_down_time_label = QLabel()
        self.low_V_label = QLabel()
        self.high_V_label = QLabel()

        self.scan_fit_num_peaks_spinbox = Qw.QSpinBox()
        self.scan_fit_num_peaks_spinbox.setRange(1,MAX_PEAKS_TO_FIT)

        # Create the buttons to step through scans
        self.next_scan_button = Qw.QPushButton("Next")
        self.prev_scan_button = Qw.QPushButton("Prev")

        # Curve fitting button
        self.peak_fit_button = Qw.QPushButton("Fit Peaks")

    def _add_widgets_to_form(self):
        # Start adding info
        self.addRow("Name", self.dma_2_name_label)

        self.addRow(TitleHLine("Run Information"))

        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Scan Details"))
        self.addRow("Scan #", self.scan_num_lineedit)
        self.addRow("Time", self.scan_timestamp_label)
        self.addRow("Low Voltage",self.low_V_label)
        self.addRow("High Voltage", self.high_V_label)
        self.addRow("Scan Up Time", self.scan_up_time_label)
        self.addRow("Scan Down Time", self.scan_down_time_label)

        self.addRow(QLabel(""))
        hbox = Qw.QHBoxLayout()
        hbox.addWidget(self.prev_scan_button)
        hbox.addWidget(self.next_scan_button)
        self.addRow(hbox)

        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Peak Fitting"))
        self.addRow("Number of peaks to fit", self.scan_fit_num_peaks_spinbox)
        self.addRow(self.peak_fit_button)

    def update_from_model(self):
        print("update_scan_widget_views: " + repr(self.model.current_scan))
        self.dma_2_name_label.setText(self.model.setup.basefilename)
        if self.model.current_scan is not None:
            #TODO - Remove these from current_scan and into ScanParms
            self.scan_num_lineedit.setText(str(self.model.setup.scan_params.scan_id_from_data))
            self.scan_timestamp_label.setText(self.model.setup.scan_params.time_stamp.strftime("%H:%M:%S"))
            self.low_V_label.setText("{:.0f}".format(self.model.setup.scan_params.low_V))
            self.high_V_label.setText("{:.0f}".format(self.model.setup.scan_params.high_V))
            self.scan_up_time_label.setText("{:.0f}".format(self.model.setup.scan_params.scan_up_time))
            self.scan_down_time_label.setText("{:.0f}".format(self.model.setup.scan_params.scan_down_time))
        else:
            self.scan_num_lineedit.setText("")
            self.scan_timestamp_label.setText("00:00:00")
            self.low_V_label.setText("0")
            self.high_V_label.setText("0")
            self.scan_up_time_label.setText("")
            self.scan_down_time_label.setText("")
