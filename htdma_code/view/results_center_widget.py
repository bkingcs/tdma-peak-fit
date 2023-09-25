import PySide2.QtWidgets as Qw
from PySide2.QtWidgets import QFrame, QTableView

from htdma_code.model.model import Model


class Total_Results_Center_Frame(QFrame):
    def __init__(self, parent, model: Model):
        super().__init__(parent)

        self.model = model

        self.total_results_table = QTableView()
        self.total_results_table.setModel(self.model.total_results_table)

        layout = Qw.QVBoxLayout()
        layout.addWidget(self.total_results_table)

        self.setLayout(layout)

