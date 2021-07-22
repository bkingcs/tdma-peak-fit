"""
This class encapsulates DMA 1, including all of the parameters used by it, and
dealing with generating the theoretical plot
"""
import matplotlib.pyplot as plt
import numpy as np
import scipy
import pandas as pd
import matplotlib as mpl
import seaborn as sns
import math
from matplotlib.ticker import FormatStrFormatter

from setup import Setup
from samples import Samples
from sample import Sample

# ELEM_CHARGE is the elementary charge of a particle in Columb.
# Coulumb is in m-kg-sec, so multiply by 1e5 to get in our cm-g-sec
# THEN, 1 Columb = 10^-1 statcoulumb, so multiply by 10
#ELEM_CHARGE = 1.602e-19 * 1e5
ELEM_CHARGE = 1.602e-19 * 1e5 * 1e1
#ELEM_CHARGE = 1.602176634e-19 * 10e5

# From wikipedia - proper value for cgs.... statcoulumbs?!?!
#ELEM_CHARGE = 4.80320425e-10

#TODO ERROR! Verify ELEM_CHARGE value. Something seems incorrect

"""
See the following for an example of what dp should be for certain dma values
https://www.tandfonline.com/doi/full/10.1080/02786826.2019.1642443
"""
def lpm_to_cm3_per_sec(lpm):
    """
    Convert liters per minute to cubic cm per second

    :param lpm: A flow specified in liters per minute
    :return: The same flow in cubic cm per second
    """
    return lpm*1000/60

class DMA_1:
    """
    DMA_1 -
    """
    def __init__(self, setup: Setup, samples: Samples, debug=False):
        self.setup = setup
        sample = samples.get_sample(0)

        if debug:
            # MF-DMA settings
            # sample.q_sh_lpm = 25
            # sample.q_aIn_lpm = 5
            # sample.q_aOut_lpm = 5
            # sample.q_excess_lpm = 25
            # self.setup.dma_1.length_cm = 49.5 #Long
            # self.setup.dma_1.radius_in_cm = 3.6
            # self.setup.dma_1.radius_out_cm = 4.6

            # TSI 3080
            sample.q_sh_lpm = 10.0
            sample.q_aIn_lpm = 1.0
            sample.q_aOut_lpm = 1.0
            sample.q_excess_lpm = 10.0
            self.setup.dma_1.length_cm = 44.44
            self.setup.dma_1.radius_in_cm = 0.937
            self.setup.dma_1.radius_out_cm = 1.958

            self.setup.params.mean_free_path_m = 68 * 1e-9
            self.setup.params.mu_gas_viscosity_Pa_sec = 0.0001837 * 1e-1

        # We're copying these over for simplicity purposes
        self.q_sh_lpm = sample.q_sh_lpm
        self.q_aIn_lpm = sample.q_aIn_lpm
        self.q_aOut_lpm = sample.q_aOut_lpm
        self.q_excess_lpm = sample.q_excess_lpm

        # Create some internal private variables for computation purposes
        self._q_sh_cm3_sec = lpm_to_cm3_per_sec(sample.q_sh_lpm)
        self._q_aIn_cm3_sec = lpm_to_cm3_per_sec(sample.q_aIn_lpm)
        self._q_aOut_cm3_sec = lpm_to_cm3_per_sec(sample.q_aOut_lpm)
        self._q_excess_cm3_sec = lpm_to_cm3_per_sec(sample.q_excess_lpm)

        # 1 P = 10 Pa * s
        self.mu_gas_viscosity_poise = self.setup.params.mu_gas_viscosity_Pa_sec * 1e1

        # We want nanometers from meters
        self.mean_free_path_nm = self.setup.params.mean_free_path_m * 1e9

        # Other parameters that need to be set by the user
        self.voltage = None

        # dp distribution computed
        self.dp_center = None
        self.dp_left_bottom = None
        self.dp_right_bottom = None

    def __repr__(self):
        s = "q_sh = {:.1f} lpm {:.2f} cm3/sec\n".format(self.q_sh_lpm,self._q_sh_cm3_sec)
        s += "q_aIn = {:.1f} lpm {:.2f} cm3/sec\n".format(self.q_aIn_lpm,self.q_aIn_lpm)
        s += "q_aOut = {:.1f} lpm {:.2f} cm3/sec\n".format(self.q_aOut_lpm,self.q_aOut_lpm)
        s += "q_excess = {:.1f} lpm {:.2f} cm3/sec\n".format(self.q_excess_lpm,self._q_excess_cm3_sec)
        s += "gas viscosity = {:.7f} Poise\n".format(self.mu_gas_viscosity_poise)
        s += "mean free path = {:.3f} nm\n".format(self.mean_free_path_nm)
        if self.voltage:
            s += "Voltage = {:.1f} V\n".format(self.voltage)
            if self.dp_center:
                s += "dp {:.1f} nm\n".format(self.dp_center)
            else:
                s += "dp not computed\n"
        else:
            s += "No voltage set\n"
        s += "WILL USE:\n"
        s += "dma1 length: {:.3f} cm\n".format(self.setup.dma_1.length_cm)
        s += "dma1 radius In {:.3f} cm\n".format(self.setup.dma_1.radius_in_cm)
        s += "dma1 radius Out {:.3f} cm\n".format(self.setup.dma_1.radius_out_cm)

        return s

    def set_voltage(self,v: float):
        """
        Set or update the voltage used to compute a new dp value
        :param v:
        :return:
        """
        if v != self.voltage:
            self.voltage = v
            self.dp_center = None
            self.dp_left_bottom = None
            self.dp_right_bottom = None

    def compute_theoretical_dist(self,init_Cs=2,n_ch=1,verbose=False):
        """
        Compute the theoretical distribution of DMA 1 based on parameters encapsulated
        inside this object. This includes computing the center dp value, and the full width
        half height values.

        :param init_Cs: The initial value of Cunningham slip specified. For most
        problems the default of 2 is acceptable
        :param n_ch:    number of elementary charges on particle
        :param verbose: Debug output

        :return: Nothing. All values computed are stored in the object
        """

        # Start by computing the center of electrical mobility Zp
        # and the corresponding full-width half-height value
        (Zp, Zp_fwhh) = self._compute_Zp()

        if verbose:
            print("Zp = {}, Zp_fwhh = {}".format(Zp, Zp_fwhh))

        Cs = init_Cs  # Initial value for Cs

        # Now, compute the corresponding dp
        self.dp_center = self._Zp_to_Dp(Zp, Cs=init_Cs,n_ch=n_ch,verbose=verbose)

        if verbose:
            print("Dp (init value of Cs = 2) = {}".format(self.dp_center))

        # Compute the bottom points for the triangle. NOTE - electrical mobility
        # and dp have an inverse relationship. Thus, we are flipping these (i.e.
        # adding to the center to get the left, vice versa for right)
        self.dp_left_bottom = self._Zp_to_Dp(Zp+Zp_fwhh,Cs=init_Cs,n_ch=n_ch,verbose=verbose)
        self.dp_right_bottom = self._Zp_to_Dp(Zp-Zp_fwhh,Cs=init_Cs,n_ch=n_ch,verbose=verbose)

    def _compute_Zp(self):
        """
        INTERNAL FUNCTION -
        Compute Zp - the center of electrical mobility, and the full width
        half height value (fwhh)

        :return: (Zp, full_width_half_height)
        """
        delta_axial = (self.setup.dma_1.length_cm * self.voltage) / np.log(self.setup.dma_1.radius_out_cm/self.setup.dma_1.radius_in_cm)
        # delta_axial = (DMA_Length_cm * V) / np.log(Radius_outer_cm/Radius_inner_cm)
        Zp_center  = (self._q_sh_cm3_sec + self._q_excess_cm3_sec) / (4 * math.pi * delta_axial)
        Zp_fwhh    = (self._q_aIn_cm3_sec + self._q_aOut_cm3_sec) / (self._q_sh_cm3_sec + self._q_excess_cm3_sec) * Zp_center
        return (Zp_center, Zp_fwhh)

    def _Zp_to_Dp(self,Zp,Cs,n_ch,verbose):
        """
        This function computes the particle diameter Dp in nanometers from
        electrical mobility Zp.

        This calculation is all from DMA literature based on quite a number
        of variables. However, what we're going to do is a bit of a
        kludgy close approximation in the Cunningham slip correction, Cs.
        It itself a function of Dp, thus making this equation rather
        non-straightforward to compute.

        :param Zp:      center of electrical mobility
        :param Cs:      Cunningham slip correction
        :param n_ch:    number of elementary charges on particle
        :param verbose: True if printing progress to console, False to suppress
        :return:        The particle diameter Dp related to the specified Zp
        """

        def _compute_dp():
            """
            THis is an internal helper function - never meant to be called
            outside of the main function!
            :return:
            """
            dp = (n_ch * ELEM_CHARGE * Cs) / (3 * math.pi * self.mu_gas_viscosity_poise * Zp)
            #dp *= 1e7 # convert from cm to nm
            #TODO ERROR! This is not the correct conversion!
            dp *= 1e7 * 1e1
            return dp

        # For the time, we're going to iterate back and forth until we converge
        # in on an answer:
        DELTA_DP = 0.1
        MAX_ITERATIONS = 1000
        MIN_DP_CHECK = 1
        MAX_DP_CHECK = 15000
        step_num = 0
        dp = _compute_dp()

        while True:
            Cs = self._Cunningham_slip_correction(dp)
            last_dp = dp
            dp = _compute_dp()
            if dp < MIN_DP_CHECK:
                raise ValueError("Zp_to_dp: {:.1f} too small. Check input values".format(dp))
            if dp > MAX_DP_CHECK * 10:
                raise ValueError("Zp_to_dp: {:.1f} too large. Check input values".format(dp))
            if math.fabs(last_dp - dp) < DELTA_DP:
                break
            step_num += 1
            if step_num > MAX_ITERATIONS:
                raise ValueError("Zp_to_dp: too many iterations!")

            if verbose:
                print("Cs (pass {}) = {}".format(step_num,Cs))
                print("Dp (pass {}) = {}".format(step_num,dp))

        if dp > MAX_DP_CHECK:
            raise ValueError("Zp_to_dp: {:.1f} too large. Check input values".format(dp))

        return dp

    def _Cunningham_slip_correction(self,dp):
        """
        Compute the Cunningham slip correction factor based on a specified
        particle diameter, dp, specified in nanometers.
        """

        Cs = 1 + (self.mean_free_path_nm / dp) * \
             (2.34 + 1.05*math.exp(-0.39 * (dp/self.mean_free_path_nm)))
        return Cs

    def get_dp(self):
        """
        Return the computed center dp. If it wasn't computed yet, then an exception
        is thrown
        """
        if not self.dp_center:
            raise ValueError("ERROR - dp not computed yet, or voltage changed without computing new dp")
        return self.dp_center

    def plot(self):
        """
        Create the distribution plot for DMA 1

        :param ax:
        :return: Figure, Axes
        """
        fig = plt.figure(figsize=(8, 6))
        ax = plt.axes()
        plt.style.use('seaborn-whitegrid')

        x = [self.dp_left_bottom, self.dp_center, self.dp_right_bottom]
        y = [0, 1, 0]

        # TODO - Fix the center height

        ax.set_xscale('log')
        ax.set_xlim(200, 1000)
        ax.set_xticks(np.arange(200, 1000, 100))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))

        # TODO - Set "Dp" for x axis label
        ax.set_ylim(0, 1)

        plt.title("DMA 1 theoretical distribution")
        plt.plot(x, y)
        plt.grid(True)

        return fig, ax

