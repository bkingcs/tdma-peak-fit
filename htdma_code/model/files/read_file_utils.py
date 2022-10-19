"""
read_file_utils - contains all of the helper methods for reading run and scan
information from files
"""

import numpy as np
import pandas as pd
import csv
import sys
import math

#Let's define hard coded rows for info

# Row info for TSI 3080 output
ROW_DMA_RADIUS_IN = 3
KEY_DMA_RADIUS_IN = "DMA Inner Radius"
ROW_DMA_RADIUS_OUT = 4
KEY_DMA_RADIUS_OUT = "DMA Outer Radius"
ROW_DMA_LENGTH = 5
KEY_DMA_LENGTH = "DMA Characteristic Length"
ROW_DMA_GAS_VISCOSITY = 7   # In Pa*sec, 1 = 10 Poise
KEY_DMA_GAS_VISCOSITY = "Reference Gas Viscosity"
ROW_DMA_MEAN_FREE_PATH = 8  # In m, so * 1e9 for nm
KEY_DMA_MEAN_FREE_PATH = "Reference Mean Free Path"
ROW_DMA_REF_TEMP = 9        # In Kelvin
KEY_DMA_REF_TEMP = "Reference Gas Temperature"
ROW_DMA_REF_PRES = 10       # In kPa
KEY_DMA_REF_PRES = "Reference Gas Pressure"
ROW_DMA_MULT_CHARGE_CORRECTION = 12
KEY_DMA_MULT_CHARGE_CORRECTION = "Multiple Charge Correction"
ROW_DMA_GAS_DENSITY = 15
KEY_DMA_GAS_DENSITY = "Gas Density"
DEF_DMA_GAS_DENSITY = 0.0012

ROW_OFFSET_SCAN_UP_TIME = 1
KEY_SCAN_UP_TIME = "Scan Up Time(s)"
ROW_OFFSET_SCAN_RETRACE_TIME = 2
KEY_SCAN_RETRACE_TIME = "Retrace Time(s)"
ROW_OFFSET_SHEATH_FLOW = 6
KEY_SHEATH_FLOW = "Sheath Flow(lpm)"
ROW_OFFSET_AEROSOL_IN_FLOW = 7
KEY_AEROSOL_IN_FLOW = "Aerosol Flow(lpm)"
ROW_OFFSET_CPC_INLET_FLOW = 8
KEY_CPC_INLET_FLOW = "CPC Inlet Flow(lpm)"
ROW_OFFSET_CPC_SAMPLE_FLOW = 9
KEY_CPC_SAMPLE_FLOW = "CPC Sample Flow(lpm)"
ROW_OFFSET_LOW_V = 10
KEY_LOW_V = "Low Voltage"
ROW_OFFSET_HIGH_V = 11
KEY_HIGH_V = "High Voltage"
ROW_OFFSET_LOW_DP_NM = 12
KEY_LOW_DP_NM = "Lower Size(nm)"
ROW_OFFSET_HIGH_DP_NM = 13
KEY_HIGH_DP_NM = "Upper Size(nm)"
ROW_OFFSET_STATUS = 16
KEY_STATUS = "Status Flag"
ROW_OFFSET_TOTAL_CONC = 25
KEY_TOTAL_CONC = "Total Concentration"

DATA_FILE_VERSION_1 = 1
DATA_FILE_VERSION_2 = 2

start_dp_row = -1
end_dp_row = -1
start_scan_data_row = -1
end_scan_data_row = -1
data_file_version = -1


def read_setup(filename: str) -> dict:
    """
    Read in the first 18 rows of the data file using pandas read_csv

    Params:
    * filename - a string representing the file to read in

    Returns:
    * A pandas DataFrame containing the keyed info we need
    """

    dict_result = {}
    row_num = 0
    global start_scan_data_row, end_scan_data_row, start_dp_row, end_dp_row, data_file_version

    # Let's assume the data file version is original
    data_file_version = DATA_FILE_VERSION_1

    with open(filename, mode='r') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for row in reader:
            row_num += 1
            #print(row_num, row)

            if "AIM Version" in row[0]:
                data_file_version = DATA_FILE_VERSION_2
            elif KEY_DMA_RADIUS_IN in row[0]:
                val = float(row[1])
                if data_file_version == DATA_FILE_VERSION_1:
                    val *= 100 # kludge fix because of cm vs. m bug?
                dict_result["DMA_1_RADIUS_IN_CM"] = val
            elif KEY_DMA_RADIUS_OUT in row[0]:
                val = float(row[1])
                if data_file_version == DATA_FILE_VERSION_1:
                    val *= 100 # kludge fix because of cm vs. m bug?
                dict_result["DMA_1_RADIUS_OUT_CM"] = val
            elif KEY_DMA_LENGTH in row[0]:
                val = float(row[1])
                if data_file_version == DATA_FILE_VERSION_1:
                    val *= 100
                dict_result["DMA_1_LENGTH_CM"] = val
            elif KEY_DMA_GAS_VISCOSITY in row[0]:
                dict_result["MU_GAS_VISCOSITY_Pa_Sec"] = float(row[1])
            elif KEY_DMA_GAS_DENSITY in row[0]:
                dict_result["GAS_DENSITY"] = float(row[1])
            elif KEY_DMA_MEAN_FREE_PATH in row[0]:
                dict_result["MEAN_FREE_PATH_M"] = float(row[1])
            elif KEY_DMA_REF_TEMP in row[0]:
                dict_result["REF_TEMP_K"] = float(row[1])
            elif KEY_DMA_REF_PRES in row[0]:
                dict_result["REF_PRES_kPa"] = float(row[1])
            elif "Sample #" in row[0]:
                start_scan_data_row = row_num
            elif "Diameter Midpoint" in row[0]:
                start_dp_row = row_num + 1
            elif "Scan" in row[0] and "Time" in row[0]:
                end_dp_row = row_num - 1
            elif data_file_version == DATA_FILE_VERSION_1 and "Total Concentration" in row[0]:
                end_scan_data_row = row_num
            elif data_file_version == DATA_FILE_VERSION_2 and "Total Conc." in row[0]:
                end_scan_data_row = row_num

    # Checking for gas density, since some files sent over did not include this...
    if "GAS_DENSITY" not in dict_result:
        dict_result["GAS_DENSITY"] = DEF_DMA_GAS_DENSITY

    # df = pd.read_csv(filename,
    #                  header=None,
    #                  sep='\t',
    #                  index_col=0,
    #                  nrows=18,
    #                  encoding = "ISO-8859-1")

    # dict_result = {}
    # NOTE - The downloaded file shows this as cm, but the numbers in the file are clearly m
    # self.dma_1.radius_in_cm = float(df.iloc[ROW_DMA_RADIUS_IN,0])
    # self.dma_1.radius_out_cm = float(df.iloc[ROW_DMA_RADIUS_OUT,0])
    # self.dma_1.length_cm = float(df.iloc[ROW_DMA_LENGTH, 0])
    # dict_result["DMA_1_RADIUS_IN_CM"] = float(df.iloc[ROW_DMA_RADIUS_IN, 0]) * 100
    # dict_result["DMA_1_RADIUS_OUT_CM"] = float(df.iloc[ROW_DMA_RADIUS_OUT,0]) * 100
    # dict_result["DMA_1_LENGTH_CM"] = float(df.iloc[ROW_DMA_LENGTH, 0]) * 100
    #
    # dict_result["MU_GAS_VISCOSITY_Pa_Sec"] = float(df.iloc[ROW_DMA_GAS_VISCOSITY])
    # dict_result["GAS_DENSITY"] = float(df.iloc[ROW_DMA_GAS_DENSITY])
    # dict_result["MEAN_FREE_PATH_M"] = float(df.iloc[ROW_DMA_MEAN_FREE_PATH])
    # dict_result["REF_TEMP_K"] = float(df.iloc[ROW_DMA_REF_TEMP])
    # dict_result["REF_PRES_kPa"] = float(df.iloc[ROW_DMA_REF_PRES])

    return dict_result

def read_scans_into_dataframe(filename: str) -> (pd.DataFrame, int):
    """
    Read in all of the scans for a given run

    Params:
    * filename - the name of the file to process

    Returns:
        (df, num_dp_values) tuple, where
        * df - pandas DataFrame containing all scans for the run
        * num_dp_values - an int specifying the number of diameters captured from the file
    """

    global start_scan_data_row, end_scan_data_row, start_dp_row, end_dp_row, data_file_version
    if start_scan_data_row == -1:
        sys.exit("Error! Unable to locate first row of scans!")

    df = pd.read_csv(filename,
                        header=0,
                        sep='\t',
                        index_col=0,
                        skiprows=start_scan_data_row-1,
                        nrows=end_scan_data_row-start_scan_data_row, # Remember, first row is the column header
                        encoding="ISO-8859-1")

    # The new version puts extra columns in! Argh!!!! More absurdness.
    columns_to_drop = []
    if data_file_version == DATA_FILE_VERSION_2:
        for col in df.columns:
            if "Unnamed" in col:
                columns_to_drop.append(col)
        if len(columns_to_drop) > 0:
            df = df.drop(labels=columns_to_drop,axis=1)

        # Rename columns to map them to the original
        df = df.rename(index={"Scan Time (s)": KEY_SCAN_UP_TIME,
                   "Retrace Time (s)" : KEY_SCAN_RETRACE_TIME,
                   "Sheath Flow (L/min)" : KEY_SHEATH_FLOW,
                   "Aerosol Flow (L/min)" : KEY_AEROSOL_IN_FLOW,
                   "Low Voltage (V)" : KEY_LOW_V,
                   "High Voltage (V)" : KEY_HIGH_V,
                   "Lower Size (nm)" : KEY_LOW_DP_NM,
                   "Upper Size (nm)" : KEY_HIGH_DP_NM,
                   "Diameter Midpoint (nm)" : "Diameter Midpoint"
                })

    # All files need to have total concentration standardized
    for ind in df.index:
        if "Total Conc" in ind:
            df = df.rename(index={ind : KEY_TOTAL_CONC})

    # Set up a uniform timestamp for each scan
    ts = pd.to_datetime(df.apply(lambda col: col["Date"] + " " + col["Start Time"], axis=0))
    df.loc["Date", :] = ts
    df = df.drop(index=["Start Time"])
    df = df.drop(index=["Diameter Midpoint"])

    if data_file_version == DATA_FILE_VERSION_2:
        # This version has some extra rows up at the top we're not using at the moment
        df = df.drop(index=["Sample Temp (C)",
                            "Sample Pressure (kPa)",
                            "Relative Humidity (%)",
                            "Mean Free Path (m)",
                            "Gas Viscosity (Pa*s)"
                            ])

    num_dp_values = end_dp_row - start_dp_row + 1

    #verison 2 -need ot deal with status, comment, and aerosol out, cpc sample
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

    global start_scan_data_row, end_scan_data_row, start_dp_row, end_dp_row, data_file_version

    num_dp_values = end_dp_row - start_dp_row + 1

    dict_result = {}
#    dict_result["SCAN_UP_TIME"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_SCAN_UP_TIME, scan_num])
    dict_result["SCAN_UP_TIME"] = float(df_scans.loc[KEY_SCAN_UP_TIME][scan_num])
#    dict_result["SCAN_DOWN_TIME"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_SCAN_RETRACE_TIME, scan_num])
    dict_result["SCAN_DOWN_TIME"] = float(df_scans.loc[KEY_SCAN_RETRACE_TIME][scan_num])
#    dict_result["SCAN_SHEATH_FLOW_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_SHEATH_FLOW, scan_num])
    dict_result["SCAN_SHEATH_FLOW_LPM"] = float(df_scans.loc[KEY_SHEATH_FLOW][scan_num])
#    dict_result["SCAN_AEROSOL_IN_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_AEROSOL_IN_FLOW, scan_num])
    dict_result["SCAN_AEROSOL_IN_LPM"] = float(df_scans.loc[KEY_AEROSOL_IN_FLOW][scan_num])
#    dict_result["SCAN_LOW_V"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_LOW_V, scan_num])
    dict_result["SCAN_LOW_V"] = float(df_scans.loc[KEY_LOW_V][scan_num])
#    dict_result["SCAN_HIGH_V"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_HIGH_V, scan_num])
    dict_result["SCAN_HIGH_V"] = float(df_scans.loc[KEY_HIGH_V][scan_num])
#    dict_result["SCAN_LOW_DP_NM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_LOW_DP_NM, scan_num])
    dict_result["SCAN_LOW_DP_NM"] = float(df_scans.loc[KEY_LOW_DP_NM][scan_num])
#    dict_result["SCAN_HIGH_DP_NM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_HIGH_DP_NM, scan_num])
    dict_result["SCAN_HIGH_DP_NM"] = float(df_scans.loc[KEY_HIGH_DP_NM][scan_num])
    dict_result["SCAN_TOTAL_CONC"] = float(df_scans.loc[KEY_TOTAL_CONC][scan_num])

    if data_file_version == DATA_FILE_VERSION_1:
        dict_result["SCAN_AEROSOL_OUT_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_CPC_INLET_FLOW, scan_num])
        dict_result["SCAN_CPC_SAMPLE_LPM"] = float(df_scans.iat[num_dp_values + ROW_OFFSET_CPC_SAMPLE_FLOW, scan_num])
        dict_result["SCAN_STATUS"] = str(df_scans.iat[num_dp_values + ROW_OFFSET_STATUS, scan_num])
    elif data_file_version == DATA_FILE_VERSION_2:
        dict_result["SCAN_AEROSOL_OUT_LPM"] = dict_result["SCAN_AEROSOL_IN_LPM"]
        dict_result["SCAN_CPC_SAMPLE_LPM"] = dict_result["SCAN_AEROSOL_IN_LPM"]
        dict_result["SCAN_STATUS"] = "N/A"

    return dict_result
