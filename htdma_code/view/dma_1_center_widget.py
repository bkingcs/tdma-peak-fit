from PySide2.QtCore import Qt
import PySide2.QtWidgets as Qw
from PySide2.QtWidgets import QFrame

from htdma_code.model.model import Model
from htdma_code.view.dma_1_graph import DMA_1_Graph_Widget
from htdma_code.view.scan_data_graph import Scan_Data_Graph_Widget

class DMA_1_Center_Frame(QFrame):

    def __init__(self, parent, model: Model):
        super().__init__(parent)

        self.model = model

        self.dma_1_graph_widget = DMA_1_Graph_Widget(model)
        self.scan_data_graph_widget = Scan_Data_Graph_Widget(model)

        self.splitter = Qw.QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.dma_1_graph_widget)
        self.splitter.addWidget(self.scan_data_graph_widget)

        layout = Qw.QVBoxLayout()
        layout.addWidget(self.splitter)

        # THe Qt way - a layout always needs a dummy widget
        self.setLayout(layout)

    def update_from_model(self):
        self.update()
        self.dma_1_graph_widget.update_plot()
        self.scan_data_graph_widget.update_plot()

    def update_dma_1_graph_from_model(self):
        self.dma_1_graph_widget.update_plot()

    def update_scan_data_graph_from_model(self):
        self.scan_data_graph_widget.update_plot()