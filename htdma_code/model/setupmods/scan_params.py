
import numpy as np
import pandas as pd

from htdma_code.model.files.read_file_utils import extract_scan_params


class ScanParams:

    def __init__(self, df: pd.DataFrame, scan_index: int) -> None:
        """
        Constructor for a ScanParams. It takes a single columb from the time stamp
        right through the end of the column and extracts out all of the parameters
        for the given Scan

        :param df: A pandas DataFrame representing all scans from a given run
        :parm scan_index: An integer index value used to select the scan of interest
        """

        self.scan_id_from_data = int(df.columns[scan_index])
        self.time_stamp = df.iat[0,scan_index]

        # Extract out the other parameters
        d_params = extract_scan_params(df,scan_num=scan_index)

        # Store them from the returned dictionary
        self.scan_up_time = d_params["SCAN_UP_TIME"]
        self.scan_down_time = d_params["SCAN_DOWN_TIME"]
        self.q_sh_lpm = d_params["SCAN_SHEATH_FLOW_LPM"]
        self.q_aIn_lpm = d_params["SCAN_AEROSOL_IN_LPM"]
        self.q_aOut_lpm = d_params["SCAN_AEROSOL_OUT_LPM"]
        self.q_cpc_sample_lpm = d_params["SCAN_CPC_SAMPLE_LPM"]
        self.low_V = d_params["SCAN_LOW_V"]
        self.high_V = d_params["SCAN_HIGH_V"]
        self.low_dp_nm = d_params["SCAN_LOW_DP_NM"]
        self.high_dp_nm = d_params["SCAN_HIGH_DP_NM"]
        self.status = d_params["SCAN_STATUS"]
        self.total_conc = d_params["SCAN_TOTAL_CONC"]

        # Validate the setup. Check whether the setup is symmetric or not
        self.is_symmetric = True
        self.q_excess_lpm = self.q_sh_lpm
        if self.q_aIn_lpm != self.q_aOut_lpm:
            self.is_symmetric = False
            self.q_excess_lpm = self.q_sh_lpm + self.q_aIn_lpm - self.q_aOut_lpm


    def __repr__(self):
        s = "scan #: {}\n".format(self.scan_id_from_data)
        s += "scan up (sec): {}\n".format(self.scan_up_time)
        s += "scan down (sec): {}\n".format(self.scan_down_time)
        s += "low V: {}\n".format(self.low_V)
        s += "high V: {}\n".format(self.high_V)
        s += "low dp: {}\n".format(self.low_dp_nm)
        s += "high dp: {}\n".format(self.high_dp_nm)
        s += "q_sh_lpm (lpm): {}\n".format(self.q_sh_lpm)
        s += "q_aIn_lpm (polydisperse) (lpm): {}\n".format(self.q_aIn_lpm)
        s += "q_aOut_lpm (monodisperse) (lpm): {}\n".format(self.q_aOut_lpm)
        s += "total conc: {}\n".format(self.total_conc)
        s += "STATUS: {}\n".format(self.status)

        return s
