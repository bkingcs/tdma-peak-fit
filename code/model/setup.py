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
            self.radius_in_cm = 0
            self.radius_out_cm = 0
            self.length_cm = 0

        def __repr__(self):
            s = "DMA 1\n"
            if self.radius_in_cm > 0:
                s += "  r_in_cm: {:.3f}\n".format(self.radius_in_cm)
                s += "  r_out_cm: {:.3f}\n".format(self.radius_out_cm)
                s += "  length_cm: {:.3f}\n".format(self.length_cm)
            else:
                s += "  NOT INITIALIZED\n"
            return s

    class Params:
        def __init__(self):
            self.mu_gas_viscosity_Pa_sec = 0
            self.gas_density = 0
            self.mean_free_path_m = 0
            self.temp_k = 20 + 273.15
            self.pres_kPa = 101.3

        def __repr__(self):
            s = "Parameters:\n"
            if self.mu_gas_viscosity_Pa_sec > 0:
                s += "  gas viscosity: {}\n".format(self.mu_gas_viscosity_Pa_sec)
                s += "  gas density: {}\n".format(self.gas_density)
                s += "  mean free path: {}\n".format(self.mean_free_path_m)
                s += "  temp (K): {}\n".format(self.temp_k)
                s += "  pres (kPa): {}\n".format(self.pres_kPa)
            else:
                s += "  NOT INITIALIZED\n"
            return s

    def __init__(self):
        self.dma_1 = self.DMA()
        self.params = self.Params()

    def __repr__(self):
        return repr(self.dma_1) + repr(self.params)

    def read_file(self, filename):
        # Read in the first 18 rows of the data file
        df_dma_1_info = pd.read_csv(filename,
                         header=None,
                         sep='\t',
                         index_col=0,
                         nrows=18)

        # NOTE - The downloaded file shows this as cm, but the numbers in the file are clearly m
        # self.dma_1.radius_in_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_IN,0])
        # self.dma_1.radius_out_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_OUT,0])
        # self.dma_1.length_cm = float(df_dma_1_info.iloc[ROW_DMA_LENGTH, 0])
        self.dma_1.radius_in_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_IN,0]) * 100
        self.dma_1.radius_out_cm = float(df_dma_1_info.iloc[ROW_DMA_RADIUS_OUT,0]) * 100
        self.dma_1.length_cm = float(df_dma_1_info.iloc[ROW_DMA_LENGTH, 0]) * 100

        self.params.mu_gas_viscosity_Pa_sec = float(df_dma_1_info.iloc[ROW_DMA_GAS_VISCOSITY])
        self.params.gas_density = float(df_dma_1_info.iloc[ROW_DMA_GAS_DENSITY])
        self.params.mean_free_path_m = float(df_dma_1_info.iloc[ROW_DMA_MEAN_FREE_PATH])
        self.params.temp_k = float(df_dma_1_info.iloc[ROW_DMA_REF_TEMP])
        self.params.pres_kPa = float(df_dma_1_info.iloc[ROW_DMA_REF_PRES])


