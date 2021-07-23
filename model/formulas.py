"""
formulas.py

This file contains all the important formulas and calcultions for the HTDMA project

"""
import numpy as np
import math

# ELEM_CHARGE is the elementary charge of a particle in Columb.
# Columb is in m-kg-sec, so multiply by 10e5 to get in our cm-g-sec
ELEM_CHARGE = 1.602e-19 * 10e5

# MU_GAS_VISCOSITY is normal air at 20 deg C and 1 atm
# Specified in Poise, where P is g / (cm*sec)
MU_GAS_VISCOSITY = 0.0001837

# the mean free path of air, value is in nanometers
# (often referred to as lambda in literature)
MEAN_FREE_PATH_STP = 68  # nm at standard temp and 1 atm

# Advanced settings only. DMA parameters need to be specified.
# These are obtained from Table 1 in Collins et al (2004) - "The Scanning DMA Transfer Function.
DMA_Length_cm = 44.44       # L in paper
Radius_inner_cm = 0.937     # r1 in paper
Radius_outer_cm = 1.958     # r2 in paper


def lpm_to_cm3_per_sec(lpm):
    """
    Convert liters per minute to cubic cm per second

    :param lpm: A flow specified in liters per minute
    :return: The same flow in cubic cm per second
    """
    return lpm*1000/60

def compute_Zp(Q_sh, Q_aIn, Q_excess, Q_aOut, V):
    """
    Compute Zp - the center of electrical mobility, and the full width
    half height value (fwhh)

    All flows are specified in lpm

    :param Q_sh:     Sheath inlet flow rate
    :param Q_aIn:    Aerosol inlet (polydisperse) flow rate
    :param Q_excess: Excess outlet flow out
    :param Q_aOut:   Aerosol outlet (monodisperse) flow rate
    :param V:        Voltage (V)

    :return: (Zp, full_width_half_height)
    """
    delta_axial = (DMA_Length_cm * V) / np.log(Radius_outer_cm/Radius_inner_cm)
    Q_sh_corr = lpm_to_cm3_per_sec(Q_sh)
    Q_excess_corr = lpm_to_cm3_per_sec(Q_excess)
    Q_aIn_corr = lpm_to_cm3_per_sec(Q_aIn)
    Q_aOut_corr = lpm_to_cm3_per_sec(Q_aOut)
    Zp_center  = (Q_sh_corr + Q_excess_corr) / (4 * math.pi * delta_axial)
    Zp_fwhh    = (Q_aIn_corr + Q_aOut_corr) / (Q_sh_corr + Q_excess_corr) * Zp_center
    return (Zp_center, Zp_fwhh)


def Cunningham_slip_correction(dp):
    """
    Compute the Cunningham slip correction factor based on a specified
    particle diameter, dp, specified in nanometers.
    """

    Cs = 1 + (MEAN_FREE_PATH_STP / dp) * \
         (2.34 + 1.05*math.exp(-0.39 * (dp/MEAN_FREE_PATH_STP)))
    return Cs


def Zp_to_Dp(Zp,Cs = 2,n_ch = 1,verbose = False):
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
        dp = (n_ch * ELEM_CHARGE * Cs) / (3 * math.pi * MU_GAS_VISCOSITY * Zp)
        dp *= 10e7 # convert from cm to nm
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
        Cs = Cunningham_slip_correction(dp)
        last_dp = dp
        dp = _compute_dp()
        if dp < MIN_DP_CHECK:
            raise ValueError("Zp_to_dp: too small. Check input values")
        if dp > MAX_DP_CHECK:
            raise ValueError("Zp_to_dp: too large. Check input values")
        if math.fabs(last_dp - dp) < DELTA_DP:
            break
        step_num += 1
        if step_num > MAX_ITERATIONS:
            raise ValueError("Zp_to_dp: too many iterations!")

        if verbose:
            print("Cs (pass {}) = {}".format(step_num,Cs))
            print("Dp (pass {}) = {}".format(step_num,dp))

    return dp

