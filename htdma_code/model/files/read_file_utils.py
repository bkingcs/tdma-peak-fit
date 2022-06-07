"""
read_file_utils - contains all of the helper methods for reading run and scan
information from files
"""

import numpy as np
import pandas as pd
import math

#Let's define hard coded rows for info

# Row info for TSI 3080 output
ROW_DMA_RADIUS_IN = 3
ROW_DMA_RADIUS_OUT = 4
ROW_DMA_LENGTH = 5
ROW_DMA_GAS_VISCOSITY = 7   # In Pa*sec, 1 = 10 Poise
ROW_DMA_MEAN_FREE_PATH = 8  # In m, so * 1e9 for nm
ROW_DMA_REF_TEMP = 9        # In Kelvin
ROW_DMA_REF_PRES = 10       # In kPa
ROW_DMA_MULT_CHARGE_CORRECTION = 12
ROW_DMA_GAS_DENSITY = 15

ROW_OFFSET_SCAN_UP_TIME = 1
ROW_OFFSET_SCAN_RETRACE_TIME = 2
ROW_OFFSET_SHEATH_FLOW = 6
ROW_OFFSET_AEROSOL_IN_FLOW = 7
ROW_OFFSET_CPC_INLET_FLOW = 8
ROW_OFFSET_CPC_SAMPLE_FLOW = 9
ROW_OFFSET_LOW_V = 10
ROW_OFFSET_HIGH_V = 11
ROW_OFFSET_LOW_DP_NM = 12
ROW_OFFSET_HIGH_DP_NM = 13
ROW_OFFSET_STATUS = 16
ROW_OFFSET_TOTAL_CONC = 25

def read_setup(filename: str) -> dict:
    """
    Read in the first 18 rows of the data file using pandas read_csv

    Params:
    * filename - a string representing the file to read in

    Returns:
    * A pandas DataFrame containing the keyed info we need
    """
    df = pd.read_csv(filename,
                     header=None,
                     sep='\t',
                     index_col=0,
                     nrows=18,
                     encoding = "ISO-8859-1")

    dict_result = {}
    # NOTE - The downloaded file shows this as cm, but the numbers in the file are clearly m
    # self.dma_1.radius_in_cm = float(df.iloc[ROW_DMA_RADIUS_IN,0])
    # self.dma_1.radius_out_cm = float(df.iloc[ROW_DMA_RADIUS_OUT,0])
    # self.dma_1.length_cm = float(df.iloc[ROW_DMA_LENGTH, 0])
    dict_result["DMA_1_RADIUS_IN_CM"] = float(df.iloc[ROW_DMA_RADIUS_IN, 0]) * 100
    dict_result["DMA_1_RADIUS_OUT_CM"] = float(df.iloc[ROW_DMA_RADIUS_OUT,0]) * 100
    dict_result["DMA_1_LENGTH_CM"] = float(df.iloc[ROW_DMA_LENGTH, 0]) * 100

    dict_result["MU_GAS_VISCOSITY_Pa_Sec"] = float(df.iloc[ROW_DMA_GAS_VISCOSITY])
    dict_result["GAS_DENSITY"] = float(df.iloc[ROW_DMA_GAS_DENSITY])
    dict_result["MEAN_FREE_PATH_M"] = float(df.iloc[ROW_DMA_MEAN_FREE_PATH])
    dict_result["REF_TEMP_K"] = float(df.iloc[ROW_DMA_REF_TEMP])
    dict_result["REF_PRES_kPa"] = float(df.iloc[ROW_DMA_REF_PRES])

    return dict_result

def read_scans(filename: str) -> (pd.DataFrame, int):
    """
    Read in all of the scans for a given run

    Params:
    * filename - the name of the file to process

    Returns:
        (df, num_dp_values) tuple, where
        * df - pandas DataFrame containing all scans for the run
        * num_dp_values - an int specifying the number of diameters captured from the file
    """
    skiprows = 18
    df = pd.read_csv(filename,
                        header=0,
                        sep='\t',
                        index_col=0,
                        skiprows=skiprows,
                        encoding="ISO-8859-1")

    ts = pd.to_datetime(df.apply(lambda col: col["Date"] + " " + col["Start Time"], axis=0))
    df.loc["Date", :] = ts
    df = df.drop(index=["Start Time"])
    df = df.drop(index=["Diameter Midpoint"])

    i_start = np.where(df.index == "Date")[0][0]
    i_end = np.where(df.index == "Scan Up Time(s)")[0][0]
    num_dp_values = i_end - i_start - 1

    return (df, num_dp_values)

def extract_scan_params(df_scans: pd.DataFrame, scan_num=0) -> dict:
    """
    From a complete DataFrame of all scans, extract out the scan parameters
    for a specified scan

    :param df_scans: A pandas DataFrame of all of the scan data
    :param scan_num: An integer representing the scan number to extract.
                     Default is the first scan, and this is rarely necessary as most
                     runs will have the same values for every scan
    :returns: A Python dictionary mapping parameter names to their values
    """

    i_start = np.where(df_scans.index == "Date")[0][0]
    i_end = np.where(df_scans.index == "Scan Up Time(s)")[0][0]
    num_dp_values = i_end - i_start - 1

    dict_result = {}
    dict_result["SCAN_UP_TIME"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_SCAN_UP_TIME, scan_num])
    dict_result["SCAN_DOWN_TIME"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_SCAN_RETRACE_TIME, scan_num])
    dict_result["SCAN_SHEATH_FLOW_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_SHEATH_FLOW, scan_num])
    dict_result["SCAN_AEROSOL_IN_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_AEROSOL_IN_FLOW, scan_num])
    dict_result["SCAN_AEROSOL_OUT_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_CPC_INLET_FLOW, scan_num])
    dict_result["SCAN_CPC_SAMPLE_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_CPC_SAMPLE_FLOW, scan_num])
    dict_result["SCAN_LOW_V"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_LOW_V, scan_num])
    dict_result["SCAN_HIGH_V"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_HIGH_V, scan_num])
    dict_result["SCAN_LOW_DP_NM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_LOW_DP_NM, scan_num])
    dict_result["SCAN_HIGH_DP_NM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_HIGH_DP_NM, scan_num])
    dict_result["SCAN_STATUS"] = str(df_scans.iat[num_dp_values + ROW_OFFSET_STATUS, scan_num])
    dict_result["SCAN_TOTAL_CONC"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_TOTAL_CONC, scan_num])

    return dict_result
