from typing import Any

import numpy as np
import scipy
import pandas as pd
import matplotlib as mpl
import seaborn as sns
import math

# Experiment setup. Default will be symmetric flow rates
Q_sh = 10.0             # Sheath in flow rate
Q_aIn = 1.0             # Aerosol inlet flow (Polydisperse)
V = 10000.0              # Volts (allow 1-10000, anything else should be flagged)

IS_SYMMETRIC = True

# If user chooses asymmetric flows then these two need to appear as well, otherwise, they are matched as indicated:
if IS_SYMMETRIC:
    Q_excess = Q_sh
    Q_aOut = Q_aIn
else:
    # User will need to enter these if in asymmetric mode
    Q_excess = 10.0
    Q_aOut = 1.0

def validate_setup():
    """
    This function will validate all user entries before any analysis
    is completed.

    :raises: ValueError if any value is not correct

    :return:
    """
    if IS_SYMMETRIC:
        if Q_aIn != Q_aOut or Q_sh != Q_excess:
            raise ValueError("Symmetric flows not matching!")
    if Q_sh + Q_aIn != Q_excess + Q_aOut:
        raise ValueError("Mismatched inlet and outlet flows!")
    if V < 1 or V > 10000:
        raise ValueError("Voltage setting out of range")

validate_setup()

# Advanced settings only. DMA parameters need to be specified.
# These are obtained from Table 1 in Collins et al (2004) - "The Scanning DMA Transfer Function.
DMA_Length_cm = 44.44       # L in paper
Radius_inner_cm = 0.937     # r1 in paper
Radius_outer_cm = 1.958     # r2 in paper

def lpm_to_cm3_per_sec(lpm):
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

# ELEM_CHARGE is the elementary charge of a particle in Columb.
# Columb is in m-kg-sec, so multiply by 10e5 to get in our cm-g-sec
ELEM_CHARGE = 1.602e-19 * 10e5

# MU_GAS_VISCOSITY is normal air at 20 deg C and 1 atm
# Specified in Poise, where P is g / (cm*sec)
MU_GAS_VISCOSITY = 0.0001837

# the mean free path of a gas molecule, value is in nanometers
# (often referred to as lambda in literature)
MEAN_FREE_PATH_STP = 68  # nm at standard temp and 1 atm

def Cunningham_slip_correction(dp):
    """
    Compute the Cunningham slip correction factor based on a specified
    particle diameter, dp, specified in nanometers.
    """

    Cs = 1 + (MEAN_FREE_PATH_STP / dp) * \
         (2.34 + 1.05*math.exp(-0.39 * (dp/MEAN_FREE_PATH_STP)))
    return Cs


def Zp_to_Dp(Zp, Cs = 2, n_ch = 1):
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
    :return:        The particle diameter Dp related to the specified Zp
    """

    def _compute_dp():
        # ELEM_CHARGE is the elementary charge of a particle in Columb.
        # Columb is in m-kg-sec, so multiply by 10e5 to get in our cm-g-sec
        ELEM_CHARGE = 1.602e-19 * 10e5

        # MU_GAS_VISCOSITY is normal air at 20 deg C and 1 atm
        # Specified in Poise, where P is g / (cm*sec)
        MU_GAS_VISCOSITY = 0.0001837

        dp = (n_ch * ELEM_CHARGE * Cs) / (3 * math.pi * MU_GAS_VISCOSITY * Zp)
        dp *= 10e7 # convert from cm to nm
        return dp

    # For the time, we're going to iterate back and forth until we converge
    # in on an answer:
    DELTA_DP = 0.1
    MAX_ITERATIONS = 1000
    step_num = 0
    dp = _compute_dp()

    while True:
        Cs = Cunningham_slip_correction(dp)
        last_dp = dp
        dp = _compute_dp()
        if math.fabs(last_dp - dp) < DELTA_DP:
            break
        step_num += 1
        if step_num > MAX_ITERATIONS:
            raise ValueError("Zp_to_dp - too many iterations!")

        print("Cs (pass {}) = {}".format(step_num,Cs))
        print("Dp (pass {}) = {}".format(step_num,dp))

    return dp

#def main(Q_sh, Q_aIn, Q_excess, Q_aOut, V):
    # (Zp, Zp_fwhh) = compute_Zp(Q_sh, Q_aIn, Q_excess, Q_aOut, V)
    # print("Zp = {}, Zp_fwhh = {}".format(Zp, Zp_fwhh))
    #
    # Cs = 2  # Initial value for Cs
    # dp = Zp_to_Dp(Zp, Cs=2)
    # print("Dp (init value of Cs = 2) = {}".format(dp))
    #
    # # Get my points:
    #
    # # Compute the bottom points for the triangle. NOTE - electrical mobility
    # # and dp have an inverse relationship. Thus, we are flipping these (i.e.
    # # adding to the center to get the left, vice versa for right)
    # dp_left_bottom = Zp_to_Dp(Zp+Zp_fwhh)
    # dp_right_bottom = Zp_to_Dp(Zp-Zp_fwhh)
    #
    # print("left: {:.3f}".format(dp_left_bottom))
    # print("center: {:.3f}".format(dp))
    # print("right: {:.3f}".format(dp_right_bottom))

