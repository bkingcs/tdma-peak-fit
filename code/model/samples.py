"""
Samples - this class encapsulates all of the samples contained in an experiment
"""

import numpy as np
import pandas as pd

from code.model.sample import Sample

class Samples:
    """
    The Samples class - this represents all samples in the entire experiment
    """
    def __init__(self):
        self.df = None
        self.num_dp_values = 0

    def __repr__(self):
        s = "Samples:\n"
        if self.df:
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
        Read in all the samples
        """
        skiprows = 18
        self.df = pd.read_csv(filename,
                 header=0,
                 sep='\t',
                 index_col=0,
                 skiprows=skiprows)
        ts = pd.to_datetime(self.df.apply(lambda col: col["Date"] + " " + col["Start Time"], axis=0))
        self.df.loc["Date", :] = ts
        self.df = self.df.drop(index=["Start Time"])
        self.df = self.df.drop(index=["Diameter Midpoint"])
        i_start = np.where(self.df.index == "Date")[0][0]
        i_end = np.where(self.df.index == "Scan Up Time(s)")[0][0]
        self.num_dp_values = i_end - i_start - 1

    def get_num_samples(self) -> int:
        """
        Simple helper function to obtain the number of scans in this run
        """
        if self.df is not None:
            return self.df.shape[1]
        else:
            return 0

    def get_sample(self,sample_col: int) -> Sample:
        """
        This retrieves one sample, based on the sample number
        :param sample_col: The column of the sample. NOTE: this is not likely the
        same as the recorded sample number. Usually, it'll be one off (i.e. we start
        with 0. They start with 1.)

        :return: A Sample object
        """
        sample= Sample(self.df.iloc[:,[sample_col]].copy(),
                       self.num_dp_values)
        return sample

