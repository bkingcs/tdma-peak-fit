"""
ResultsTableModel - This is entirely based on some code found at:

https://www.pythonguis.com/tutorials/qtableview-modelviews-numpy-pandas/

When subclassing QAbstractTableModel , you must implement:
 * rowCount()
 * columnCount()
 * data() .
 Default implementations of the index() and parent() functions are provided by QAbstractTableModel .
 Well behaved models will also implement headerData() .
"""

from PySide2.QtCore import QAbstractTableModel, Qt
from PySide2.QtGui import QStandardItemModel

import numpy as np
import pandas as pd

from htdma_code.model.scan import Scan

class ResultsTableModel(QAbstractTableModel):

    def __init__(self):
        super(ResultsTableModel, self).__init__()
        self.df = pd.DataFrame(columns=["scan","peak","dp","height","fwhh"])

    def data(self, index, role):
        """
        REQUIRED - provides the data
        """
        if role == Qt.DisplayRole:
            value = self.df.iloc[index.row(),index.column()]
            if index.column() == 2:
                return str(np.round(value))
            if index.column() == 3 or index.column() == 4:
                return str(np.round(value,decimals=1))
            return str(value)

    def rowCount(self, index):
        return self.df.shape[0]

    def columnCount(self, index):
        return self.df.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.df.columns[section])

            if orientation == Qt.Vertical:
                return str(self.df.index[section])

    def add_scan_results(self, scan: Scan):
        if not scan.peak_fit_results:
            return

        for peak in scan.peak_fit_results:
            new_row = {}
            new_row["scan"] = scan.scan_index + 1
            new_row["peak"] = peak.index + 1
            new_row["dp"] = peak.dp
            new_row["height"] = peak.height
            new_row["fwhh"] = peak.fwhh
            self.df.loc[len(self.df)] = new_row

        # Trigger a refresh
        self.layoutChanged.emit()
