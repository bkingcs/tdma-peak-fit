import numpy as np
import pandas as pd
import scipy
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime
import seaborn as sns

from setup import Setup
from samples import Samples
from sample import Sample
from First_DMA import DMA_1

import os
#os.chdir("/Users/brk009/PycharmProjects/ChemicsCurveFit")
print(os.getcwd())

# Read in the setup info from the sample file
#filename = "TestData/0.1gL_AmmSulf_Sucrose_Internal_Mix_(6_7_21).txt"
filename = "TestData/A-Pinene_Carene_100.100.200ppb_7.14.txt"
#filename = "TestData/HTDMA_0.1gL_AmmSulf200nmPSL_Sample_Peaks.txt"
setup = Setup(filename)

print(setup)

samples = Samples(filename)
print(samples)

dma_1_theo = DMA_1(setup,samples)

print(dma_1_theo)

dma_1_theo.set_voltage(10000)
print(dma_1_theo)

dma_1_theo.compute_theoretical_dist(verbose=True)
print(dma_1_theo)

print("dp = {:.1f}".format(dma_1_theo.dp_center))

fig, ax = dma_1_theo.plot()
plt.show()

# let's grab one sample from the file

# sample_num represents the sample in the dataframe of all samples we'll extract
sample_column = 30

sample = samples.get_sample(sample_column)

print(sample)

num_peaks = 2
sample.fit(num_peaks=num_peaks,verbose=True,plot_steps = True)

sample.get_fit_peak_dp()

fig, ax = sample.plot_fit()
plt.show()