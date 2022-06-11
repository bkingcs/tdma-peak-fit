
import os
import pandas as pd

import htdma_code.model.files.read_file_utils as read_file_utils
from htdma_code.model.setupmods.dma_params import DMAParams
from htdma_code.model.setupmods.run_params import RunParams
from htdma_code.model.setupmods.scan_params import ScanParams

class Setup:
    """
    The Setup class - this encapsulates all parameters for a given run.
    """

    def __init__(self):
        #self.dma_1_params = DMAParams()
        #self.run_params = RunParams()
        self.basefilename = None
        self.dma_1_params: DMAParams = None
        self.run_params: RunParams = None
        self.num_dp_values: int = 0
        self.df_raw_scan_data:pd.DataFrame = None

        # Individual scan selected parameters
        self.scan_params: ScanParams = None
        self._current_scan_index = 0

    def __repr__(self):
        return repr(self.dma_1_params) + \
               repr(self.run_params) + \
               repr(self.scan_params)

    def read_file(self, filename: str) -> None:
        """
        Read in the data from the specified file

        :param filename: a string representing the file to read in. Must be in a
                         readable text format
        """

        # Get the name of the run
        self.basefilename = os.path.basename(filename)

        # read in the general setup info for the run
        dict_setup_info = read_file_utils.read_setup(filename)

        # Read in the scan data
        (self.df_raw_scan_data, self.num_dp_values) = read_file_utils.read_scans(filename)

        self.dma_1_params = DMAParams(length_cm=dict_setup_info["DMA_1_LENGTH_CM"],
                                      radius_in_cm=dict_setup_info["DMA_1_RADIUS_IN_CM"],
                                      radius_out_cm=dict_setup_info["DMA_1_RADIUS_OUT_CM"]
        )

        self.run_params = RunParams(mu_gas_viscosity_Pa_sec=dict_setup_info["MU_GAS_VISCOSITY_Pa_Sec"],
                                   gas_density=dict_setup_info["GAS_DENSITY"],
                                   mean_free_path_m=dict_setup_info["MEAN_FREE_PATH_M"],
                                   temp_k=dict_setup_info["REF_TEMP_K"],
                                   pres_kPa=dict_setup_info["REF_PRES_kPa"]
                                   )

        # Always reset the current scan index back to 0 if we're reading in a new file
        self._current_scan_index = 0
        self.scan_params = ScanParams(self.df_raw_scan_data, self._current_scan_index)

    def update_scan_params(self,new_scan_index):
        """
        Update the scan parameters for the selected scan to be analyzed

        :param new_scan_index: Index
        """
        self._current_scan_index = new_scan_index
        self.scan_params = ScanParams(self.df_raw_scan_data, self._current_scan_index)
