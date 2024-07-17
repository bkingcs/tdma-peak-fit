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

        self.rh_dspinbox = Qw.QDoubleSpinBox()
        self.rh_dspinbox.setDecimals(1)
        self.rh_dspinbox.setRange(0,100)

        self.scan_num_lineedit = QLineEdit()
        self.scan_num_lineedit.setText("0")

        self.scan_timestamp_label = QLabel("00:00:00")

        self.scan_up_time_label = QLabel()
        self.scan_down_time_label = QLabel()
        self.dp_range_label = QLabel()
        self.V_range_label = QLabel()
        self.total_conc_label = QLabel()

        self.scan_fit_num_peaks_spinbox = Qw.QSpinBox()
        self.scan_fit_num_peaks_spinbox.setRange(1,MAX_PEAKS_TO_FIT)

        # Create the buttons to step through scans
        self.next_scan_button = Qw.QPushButton("Next")
        self.prev_scan_button = Qw.QPushButton("Prev")

        # Peak fitting widgets
        self.num_peaks_predicted_label = QLabel()
        self.peak_fit_button = Qw.QPushButton("Fit Peaks")

        # Fit Stats
        self.resuduals_mean_label = QLabel()
        self.rmse_label = QLabel()
        self.durbin_watson_label = QLabel()

        # Allow the user to override autoscaling of y axis
        self.autoscale_y_checkbox = Qw.QCheckBox("Autoscale Y")
        self.max_y_lineedit = QLineEdit()

    def _add_widgets_to_form(self):
        # Start adding info
        self.addRow("Name", self.dma_2_name_label)

        self.addRow(TitleHLine("Run Information"))
        self.addRow("RH %",self.rh_dspinbox)

        self.addRow(QLabel(""))

        self.addRow(TitleHLine("Scan Details"))
        self.addRow("Scan #", self.scan_num_lineedit)
        self.addRow("Time", self.scan_timestamp_label)
        self.addRow("dp Range", self.dp_range_label)
        self.addRow("V Range", self.V_range_label)
        self.addRow("Scan Up Time", self.scan_up_time_label)
        self.addRow("Scan Down Time", self.scan_down_time_label)
        self.addRow("Total Conc",self.total_conc_label)

        self.addRow(QLabel(""))
        hbox = Qw.QHBoxLayout()
        hbox.addWidget(self.prev_scan_button)
        hbox.addWidget(self.next_scan_button)
        self.addRow(hbox)

        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Peak Fitting"))
        self.addRow("Predicted Peaks",self.num_peaks_predicted_label)
        self.addRow("Number of peaks to fit", self.scan_fit_num_peaks_spinbox)
        self.addRow(self.peak_fit_button)

        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Fit Quality Stats"))
        self.addRow("Residuals Mean",self.resuduals_mean_label)
        self.addRow("RMSE",self.rmse_label)
        self.addRow("Durbin-Watson",self.durbin_watson_label)

        self.addRow(QLabel(""))
        self.addRow(TitleHLine("Graphing"))
        self.addRow(self.autoscale_y_checkbox)
        self.addRow("Max Y",self.max_y_lineedit)


    def update_from_model(self):
        print("update_scan_widget_views: " + repr(self.model.current_scan))
        self.dma_2_name_label.setText(self.model.setup.basefilename)
        self.rh_dspinbox.setValue(self.model.setup.run_params.rh)
        if self.model.current_scan is not None:
            scan_params = self.model.setup.scan_params
            self.scan_num_lineedit.setText(str(scan_params.scan_id_from_data))
            self.scan_timestamp_label.setText(scan_params.time_stamp.strftime("%H:%M:%S"))
            self.dp_range_label.setText("{:.0f} - {:.0f}".format(scan_params.low_dp_nm,
                                                                 scan_params.high_dp_nm))
            self.V_range_label.setText("{:.0f} - {:.0f}".format(scan_params.low_V,
                                                                scan_params.high_V))
            self.total_conc_label.setText("{:.0f}".format(scan_params.total_conc))
            self.scan_up_time_label.setText("{:.0f}".format(self.model.setup.scan_params.scan_up_time))
            self.scan_down_time_label.setText("{:.0f}".format(self.model.setup.scan_params.scan_down_time))

            # Scan info
            self.num_peaks_predicted_label.setText(str(self.model.current_scan.num_peaks_predicted))

            # Total Fit info
            total_fit_result = self.model.current_scan.total_fit_result
            if total_fit_result:
                self.resuduals_mean_label.setText("{:.1f}".format(total_fit_result.residuals_mean))
                self.rmse_label.setText("{:.1f}".format(total_fit_result.rmse))
                self.durbin_watson_label.setText("{:.1f}".format(total_fit_result.durbin_watson))
            else:
                self.resuduals_mean_label.setText("")
                self.rmse_label.setText("")
                self.durbin_watson_label.setText("")

            # Update the maximum y scale value if autoscale is not checked
            if self.model.scan_graph_auto_scale_y is True:
                self.autoscale_y_checkbox.setChecked(True)
                self.max_y_lineedit.setEnabled(False)
                self.max_y_lineedit.setText("")
            else:
                self.autoscale_y_checkbox.setChecked(False)
                self.max_y_lineedit.setEnabled(True)
                # Show number in scientific format with 2 decimal places
                self.max_y_lineedit.setText("{:.2e}".format(self.model.scan_graph_max_y))

        else:
            self.scan_num_lineedit.setText("")
            self.scan_timestamp_label.setText("00:00:00")
            self.dp_range_label.setText("- - -")
            self.V_range_label.setText("- - -")
            self.total_conc_label.setText("0")
            self.scan_up_time_label.setText("")
            self.scan_down_time_label.setText("")
            self.num_peaks_predicted_label.setText("")
            self.resuduals_mean_label.setText("")
            self.rmse_label.setText("")
            self.durbin_watson_label.setText("")
            self.autoscale_y_checkbox.setChecked(True)
            self.max_y_lineedit.setEnabled(True)
            self.max_y_lineedit.setText("")
