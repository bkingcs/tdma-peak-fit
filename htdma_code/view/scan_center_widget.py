from PySide2.QtCore import Qt
import PySide2.QtWidgets as Qw
from PySide2.QtWidgets import QFrame, QTableWidget, QTableWidgetItem

from htdma_code.model.model import Model
from htdma_code.view.scan_data_graph import Scan_Data_Graph_Widget

class Scan_Data_Center_Frame(QFrame):

    def __init__(self, parent, model: Model):
        super().__init__(parent)

        self.model = model

        self.scan_results_table = QTableWidget()
        self.scan_results_table.setRowCount(5)
        self.scan_results_table.setColumnCount(7)
        self.scan_results_table.setHorizontalHeaderLabels(["Peak #","dp","height","fwhh","sd","growth","kappa"])

        self.scan_data_graph_widget = Scan_Data_Graph_Widget(model)

        self.splitter = Qw.QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.scan_data_graph_widget)
        self.splitter.addWidget(self.scan_results_table)

        layout = Qw.QVBoxLayout()
        layout.addWidget(self.splitter)

        # THe Qt way - a layout always needs a dummy widget
        self.setLayout(layout)

    def update_from_model(self):
        self.update()
        self.scan_data_graph_widget.update_plot()

        # Populate the table as long as a scan has been done
        peak_fit_results = self.model.current_scan.peak_fit_results
        if peak_fit_results is None:
            return

        self.scan_results_table.setRowCount(len(peak_fit_results))
        for i_peak in range(len(peak_fit_results)):
            peak = peak_fit_results[i_peak]
            self.scan_results_table.setItem(i_peak,0,QTableWidgetItem(str(peak.index+1)))
            self.scan_results_table.setItem(i_peak,1,QTableWidgetItem("{}".format(round(peak.dp))))
            self.scan_results_table.setItem(i_peak,2,QTableWidgetItem("{:.0f}".format(peak.height)))
            self.scan_results_table.setItem(i_peak,3,QTableWidgetItem("{:.1f}".format(peak.fwhh)))
            self.scan_results_table.setItem(i_peak,4,QTableWidgetItem("{:.1f}".format(peak.sd)))


