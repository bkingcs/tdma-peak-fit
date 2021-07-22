"""
Setup - this is a class that
"""

import numpy as np
import pandas as pd
import math

#Let's define hard coded rows for info
ROW_DMA_RADIUS_IN = 3
ROW_DMA_RADIUS_OUT = 4
ROW_DMA_LENGTH = 5
ROW_DMA_GAS_VISCOSITY = 7   # In Pa*sec, 1 = 10 Poise
ROW_DMA_MEAN_FREE_PATH = 8  # In m, so * 1e9 for nm
ROW_DMA_REF_TEMP = 9        # In Kelvin
ROW_DMA_REF_PRES = 10       # In kPa
ROW_DMA_MULT_CHARGE_CORRECTION = 12
ROW_DMA_GAS_DENSITY = 15
ROW_DMA_MOMENT = 17         # This should be "Number"

class Setup:
    """
    The Setup class - this encapsulates all parameters for a given run.

    It encapsulates two classes:
    * DMA - the parameters that specify the DMA.
    """
    class DMA:
        """
        Standard
        """
        def __init__(self):
            self.radius_in_cm = None
            self.radius_out_cm = None
            self.length_cm = None

        def __repr__(self):
            s = "DMA 1"
            s += "\n  r_in: {:.3f}".format(self.radius_in_cm)
            s += "\n  r_out: {:.3f}".format(self.radius_out_cm)
            s += "\n  length_cm: {:.3f}".format(self.length_cm)
            s += "\n"
            return s

    class Params:
        def __init__(self):
            self.mu_gas_viscosity_Pa_sec = None
            self.gas_density = None
            self.mean_free_path_m = None
            self.temp_k = 20 + 273.15
            self.pres_kPa = 101.3

        def __repr__(self):
            s = "Parameters:"
            s += "\n  gas viscosity: {}".format(self.mu_gas_viscosity_Pa_sec)
            s += "\n  gas density: {}".format(self.gas_density)
            s += "\n  mean free path: {}".format(self.mean_free_path_m)
            s += "\n  temp (K): {}".format(self.temp_k)
            s += "\n  pres (kPa): {}".format(self.pres_kPa)
            s += "\n"
            return s

    def __init__(self, filename: str):
        # Read in the first 18 rows of the data file
        df_dma_1_info = pd.read_csv(filename,
                         header=None,
                         sep='\t',
                         index_col=0,
                         nrows=18)
        self.dma_1 = self.DMA()

        # NOTE - The downloaded file shows this as cm, but the numbers in the file are clearly m
        self.dma_1.radius_in_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_IN,0])
        self.dma_1.radius_out_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_OUT,0])
        self.dma_1.length_cm = float(df_dma_1_info.iloc[ROW_DMA_LENGTH, 0])
        # self.dma_1.radius_in_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_IN,0]) * 100
        # self.dma_1.radius_out_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_OUT,0]) * 100
        # self.dma_1.length_cm = float(df_dma_1_info.iloc[ROW_DMA_LENGTH, 0]) * 100

        self.params = self.Params()
        self.params.mu_gas_viscosity_Pa_sec = float(df_dma_1_info.iloc[ROW_DMA_GAS_VISCOSITY])
        self.params.gas_density = float(df_dma_1_info.iloc[ROW_DMA_GAS_DENSITY])
        self.params.mean_free_path_m = float(df_dma_1_info.iloc[ROW_DMA_MEAN_FREE_PATH])
        self.params.temp_k = float(df_dma_1_info.iloc[ROW_DMA_REF_TEMP])
        self.params.pres_kPa = float(df_dma_1_info.iloc[ROW_DMA_REF_PRES])

    def __repr__(self):
        return repr(self.dma_1) + repr(self.params)
