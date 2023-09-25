
import numpy as np
import pandas as pd

import htdma_code.model.files.read_file_utils as read_file_utils
from htdma_code.model.scan import Scan

class Scans:
    """
    The Scans class

    This class encapsulates all scans in a given run. All scans are processed right from the raw data file
    and managed as a pandas DataFrame.

    Attributes:
        * df - internal Pandas dataframe storing the file contents read in
        * list_of_scans - a Python list of Scan objects
        * num_dp_values - a convenience variable that stores the numnber of channels / dp values
    """
    def __init__(self):
        self.df = None
        self.list_of_scans = None
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
        Read in all the scans, and store them internally as a Pandas dataframe
        AND as a list of scan objects
        """
        (self.df, self.num_dp_values) = read_file_utils.read_scans_into_dataframe(filename)

        # Now, process all scan data into Scan objects. Scans are stored as columns
        # in the data
        self.list_of_scans = []
        for col in range(self.df.shape[1]):
            scan = Scan(scan_index=col,
                        df=self.df.iloc[:, [col]].copy(),
                        num_dp_values=self.num_dp_values)
            self.list_of_scans.append(scan)

    def get_num_scans(self) -> int:
        """
        Simple helper function to obtain the number of scans in this run
        """
        if self.df is not None:
            return self.df.shape[1]
        else:
            return 0

    def get_scan(self, scan_index: int) -> Scan:
        """
        This retrieves one scan, based on the scan number

        :param scan_index: The column of the scan in the data frame. NOTE: this is not likely the
        same as the recorded scan number. Usually, it'll be one off (i.e. we start
        with 0. They start with 1.)

        :return: A Scan object
        """
        return self.list_of_scans[scan_index]

