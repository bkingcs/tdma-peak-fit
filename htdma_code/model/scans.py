
import numpy as np
import pandas as pd

import htdma_code.model.files.read_file_utils as read_file_utils
from htdma_code.model.scan import Scan

class Scans:
    """
    The Scans class

    This class encapsulates all scans in a given run. All scans are processed right from the raw data file
    and managed as a pandas DataFrame.

    """
    def __init__(self):
        self.df = None
        self.num_dp_values = 0

    def __repr__(self):
        s = "Scans:\n"
        if self.df is not None:
            s += "  Index: {}\n".format(repr(self.df.index))
            s += "  Columns: {}\n".format(repr(self.df.columns))
            s += "  Num Rows: {}\n".format(repr(self.df.shape[0]))
            s += "  Num Cols: {}\n".format(repr(self.df.shape[1]))
            s += "  Num dp values: {}\n".format(self.num_dp_values)
        else:
            s += "  NOT INITIALIZED"

        return s

    def read_file(self, filename):
        """
        Read in all the scans
        """
        (self.df, self.num_dp_values) = read_file_utils.read_scans(filename)

    def get_num_scans(self) -> int:
        """
        Simple helper function to obtain the number of scans in this run
        """
        if self.df is not None:
            return self.df.shape[1]
        else:
            return 0

    def get_scan(self, scan_col: int) -> Scan:
        """
        This retrieves one scan, based on the scan number

        :param scan_col: The column of the scan in the data frame. NOTE: this is not likely the
        same as the recorded scan number. Usually, it'll be one off (i.e. we start
        with 0. They start with 1.)

        :return: A Scan object
        """
        scan = Scan(self.df.iloc[:, [scan_col]].copy(),
                    self.num_dp_values)
        return scan

