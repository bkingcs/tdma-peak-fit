"""
This class creates a scan object stores the data from a single scan.
"""
# External Packages
import logging
import numpy as np
import scipy.stats

# Internal Packages
# from algorithm import sigmoid_fit
# import constants as const
# import fast_dp_calculator as fast_dp_calculator
# import helper_functions as hf

# Set logger for this module
logger = logging.getLogger("scan")


class Scan(object):
    """
    This class creates a scan object stores the data from a single scan.

    Raw: Original Data
    Processed: Data after shifts are processed
    Corrected: Data after charge corrections
    Cleaned: Data after sigmoid cleaning

    The following variables are stored:  # RESEARCH Confirm variable descriptions

        - **status**: status of the scan
        - **status_code**: The reason why the scan is not good
        - **counts_to_conc**: the flow rate
        - **index**: the scan #
        - **start_time**: what time the scan starts. Format is hh:mm:ss
        - **end_time**: what time the scan ends. Format is hh:mm:ss
        - **duration**: duration of the scan
        - **scan_up_time**: up and down scan time. Very useful to align the data
        - **scan_down_time**:
        - etc... # REVIEW Documentation

    :param int index: The scan number from the SMPS file.  # TODO issues/4 [Current is sequential #s from zero]

    """

    def __init__(self, index):
        # TODO issues/45 combine status and code into one
        # DOCQUESTION / RESEARCH duration = scan_up_time + scan_down_time; end time is start_time+duration. Neccessary?
        # Controller#start.create_scans()
        self.version = "2.2.5"
        self.status = 1
        self.status_code = 0
        self.sigmoid_status = None
        self.counts_to_conc = 0.0
        self.cpc_sample_flow = 0.05
        self.index = index
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.scan_up_time = 0
        self.scan_down_time = 0

        # Scan#align_smps_ccnc_data
        self.shift_factor = 0

        # RESEARCH Following variables for continued use
        # TODO issues/10
        # Controller#auto_fit_sigmoid
        self.sig_df = ""  # TODO issues/64  Will be unneccessary after dataframe switch
        self.sig_peaks_indices = []
        self.sig_selection = []
        self.sigmoid_params = []
        self.dp50 = []
        self.sigmoid_curve_x = []
        self.sigmoid_curve_y = []

        self.asym_limits = [0.75, 1.5]  # RESEARCH Magic number  RESEARCH get from controller?

    def __repr__(self):
        """
        Returns a string representation of variables stored in the the scan.  The format is: `var_name;var_value`.
        Nonprimative variables are stored as  `var_name;type(var_value)`

        :return: The scan as a string.
        :rtype: str
        """
        items = ("%s;%r" % (k, v) for k, v in list(self.__dict__.items()))
        return "%s" % "\n".join(items)

    ###############
    # Get Values  #
    ###############

    def is_valid(self):
        """
        Retuns if the scan is valid or not.

        :return: True if status == 1, otherwise False
        :rtype: bool
        """
        return self.status == 1  # TODO issues/45 affected by proposed status code change


    def get_status_code_descript(self):
        """
        Returns a string value explaining the status code of the current scan

        :return: The status code of the current scan.
        :rtype: str
        """
        if self.status_code == 0:  # RESEARCH 0 Status Code
            return "The scan shows no problem."
        elif self.status_code == 1:  # RESEARCH 1 Status Code
            return "There is no equivalent ccnc data for this scan. This is likely because ccnc data start at a later" \
                   "time than smps scan, or it ends before the smps scan."
        elif self.status_code == 2:  # RESEARCH 2 Status Code
            return "The length of SMPS for this scan does not agree with the indicated scan duration of the experiment."
        elif self.status_code == 3:  # RESEARCH 3 Status Code
            return "The distribution of SMPS and CCNC data has a low correlation with those of the next few scans."
        elif self.status_code == 4:  # RESEARCH 4 Status Code
            return "The program can not locate the reference point for SMPS data."
        elif self.status_code == 5:  # RESEARCH 5 Status Code
            return "The program can not locate the reference point for CCNC data."
        elif self.status_code == 6:  # RESEARCH 6 Status Code
            return "The scan do not have enough CCNC or SMPS data. Most likely because we shift the data too much"
        elif self.status_code == 7:  # RESEARCH 7 Status Code
            return "The supersaturation rate or temperature do not remain constant throughout the scan!"
        elif self.status_code == 8:  # RESEARCH 8 Status Code
            return "The temperature do not remain constant enough throughout the scan!"
        elif self.status_code == 9:  # RESEARCH 9 Status Code
            return "The Scan is manually disabled by the user!"
            # DOCQUESTION Where does the following play in?  Was commented out.  Looked like combined with 7? Split?
            # return "The supersaturation rate does not remain constant throughout the scan duration."

    ###############
    # Set Values  #
    ###############

    def set_start_time(self, start_time):
        """
        Sets the start_time value in the scan object.

        :param datetime.datetime start_time:  The time the scan started.  From the smps file.
        """
        self.start_time = start_time

    def set_end_time(self, end_time):
        """
        Sets the end_time value in the scan object.

        :param datetime.datetime end_time: The end time of the scan.  Typically the start time plus the duration.
        """
        self.end_time = end_time

    def set_up_time(self, up_time):
        """
        Sets the scan_up_time value in the scan object.

        :param int up_time:  The scan up time from the smps file.
        """
        self.scan_up_time = up_time

    def set_down_time(self, down_time):
        """
        Sets the scan_down_time value in the scan object.

        :param int down_time:  The scan down time from the retrace time in the smps file.
        """
        self.scan_down_time = down_time

    def set_duration(self, duration):
        """
        Sets the duration value in the scan object.

        :param int duration:  The duration of the scan. Typically this is scan_up_time + scan_down_time.
        """
        self.duration = duration


    def add_to_diameter_midpoints(self, new_data):
        """
        Adds the new_data value to the diameter_midpoints list in the scan object.

        :param str|int|float new_data: The diameter_midpoints to add to the list
        """
        self.diameter_midpoints.append(float(new_data))

    def set_status(self, status):
        """
        Sets the status value in the scan object.

        :param int status: The updated status
        """
        self.status = status

    def set_status_code(self, code):
        """
        Sets the status_code value in the scan object.

        :param int code: The updated status code
        """
        self.status_code = code

    # def set_shift_factor(self, factor):
    #     """
    #     If the factor is lless then that length of number of CCNC raw data points, it sets the shift factor to the
    #     value provided.  Otherwise it sets the shift factor to zero.
    #
    #     :param int factor: The number of data points to shift data so that the SMPS data and the CCNC data align.
    #     """
    #     if factor < len(self.raw_ccnc_counts):
    #         self.shift_factor = factor
    #     else:
    #         self.shift_factor = 0  # RESEARCH Does a 0 make sense?

    # def set_sigmoid_params(self, params):
    #     """
    #     # REVIEW Documentation
    #
    #     :param params: # REVIEW Documentation
    #     :type params: # REVIEW Documentation
    #     """
    #     # COMBAKL Sigmoid
    #     self.sigmoid_params = params
    #     self.fit_sigmoids()

    #######################
    # Validation Methods  #
    #######################

    # def pre_align_self_test(self):
    #     """
    #     Compares the length of the smps data and if it's not in the same as the duration, invalidates the scan
    #     """
    #     if len(self.raw_smps_counts) != self.duration:
    #         self.status = 0
    #         self.set_status_code(2)  # RESEARCH 2 Status Code
    #         # DOCQUESTION K: more work over here. Can always improve
    #         # DOCQUESTION K: perform Hartigan's dip test to test for bimodality

    # def post_align_self_test(self):
    #     """
    #     Checks for invalid scans.  Currently tests for:
    #
    #     - Error in supersaturation
    #     - Standard devations in the three tempuratures greater than 1
    #     - Checks for uniform values in temperatures by comparing the first value to all the values
    #
    #     """
    #     # DOCQUESTION K: more work over here. Can always improve this one
    #     # Check for error in supersaturation
    #     for i in range(len(self.processed_super_sats)):
    #         if not hf.are_floats_equal(self.true_super_sat, self.processed_super_sats[i]):  # DOCQUESTION err value?
    #             self.true_super_sat = None
    #             self.set_status(0)
    #             self.set_status_code(7)  # RESEARCH 7 Status Code
    #             break
    #     # check for standard deviation on tempuratures
    #     if np.std(self.processed_T1s) > 1 or np.std(self.processed_T2s) > 1 or np.std(self.processed_T3s) > 1:
    #         self.set_status(0)
    #         self.set_status_code(7)  # RESEARCH 7 Status Code
    #     # check for uniform values
    #     for i in range(len(self.processed_T1s)):
    #         # check for temperature 1
    #         if not hf.are_floats_equal(self.processed_T1s[0], self.processed_T1s[i], 1):
    #             self.set_status(0)
    #             self.set_status_code(7)  # RESEARCH 7 Status Code
    #         # check for temperature 2
    #         if not hf.are_floats_equal(self.processed_T2s[0], self.processed_T2s[i], 1):
    #             self.set_status(0)
    #             self.set_status_code(7)  # RESEARCH 7 Status Code
    #         # check for temperature 3
    #         if not hf.are_floats_equal(self.processed_T2s[0], self.processed_T2s[i], 1):
    #             self.set_status(0)
    #             self.set_status_code(7)  # RESEARCH 7 Status Code

    #############################
    # Data Transformation Code  #
    #############################

    # def do_basic_trans(self):
    #     """
    #     Convert lists to numpy arrays.
    #     """
    #     self.raw_T1s = np.asarray(self.raw_T1s)
    #     self.raw_T2s = np.asarray(self.raw_T2s)
    #     self.raw_T3s = np.asarray(self.raw_T3s)
    #     self.raw_smps_counts = np.asarray(self.raw_smps_counts, dtype=np.float64)
    #     self.raw_ccnc_counts = np.asarray(self.raw_ccnc_counts, dtype=np.float64)
    #     self.raw_normalized_concs = np.asarray(self.raw_normalized_concs)
    #     self.diameter_midpoints = np.asarray(self.diameter_midpoints)
    #     self.raw_ave_ccnc_sizes = np.asarray(self.raw_ave_ccnc_sizes)
    #     self.raw_super_sats = np.asarray(self.raw_super_sats)
    #     self.ave_smps_diameters = np.asarray(self.ave_smps_diameters)
    #
    # def generate_processed_data(self):  # RESEARCH should this be called apply shift?
    #     """
    #     Processing SMPS is straightforward.
    #
    #     Processing CCNC is based on the shift factor.
    #
    #     - If there is a negative shift factor, insert zeros before the CCNC data.
    #     - If there is a positive shift factor, drop the beginning rows by the shift factor.
    #     - If there is not enough data, then zeros are added to the end.
    #     - Processed data is then truncated to match the length of duration.
    #
    #     Finally the :class:`~scan.Scan.post_align_self_test` is processed to verify validity of scan.
    #
    #     Original data is stored seperately to ensure no data loss when shifting.
    #     """
    #     # Copy the raw SMPS data to ensure no data loss
    #     self.processed_smps_counts = self.raw_smps_counts
    #     # Process the dndlogdp list  # DOCQUESTION naming again
    #     self.processed_normalized_concs = hf.normalize_dndlogdp_list(self.raw_normalized_concs)
    #     # Copy raw CCNC values to local variables
    #     ccnc_counts = self.raw_ccnc_counts[:]
    #     ccnc_count_sums = self.raw_ccnc_count_sums[:]
    #     ccnc_sample_flow = self.raw_ccnc_sample_flow[:]
    #     t1s = self.raw_T1s[:]
    #     t2s = self.raw_T2s[:]
    #     t3s = self.raw_T3s[:]
    #     super_sats = self.raw_super_sats[:]
    #     ave_ccnc_sizes = self.raw_ave_ccnc_sizes[:]
    #     # Update for shift factors
    #     # -- if shift factor is non-negative  # DOCQUESTION But, we assumed it always would be?
    #     if self.shift_factor >= 0:
    #         # if not enough ccnc counts to even shift, the scan is invalid
    #         if len(ccnc_counts) < self.shift_factor:
    #             self.set_status(0)
    #             self.set_status_code(6)  # RESEARCH 6 Status Code
    #         # Shift the data based on the shift factor
    #         ccnc_counts = ccnc_counts[self.shift_factor:]
    #         ccnc_count_sums = ccnc_count_sums[self.shift_factor:]
    #         ccnc_sample_flow = ccnc_sample_flow[self.shift_factor:]
    #         t1s = t1s[self.shift_factor:]
    #         t2s = t2s[self.shift_factor:]
    #         t3s = t3s[self.shift_factor:]
    #         super_sats = super_sats[self.shift_factor:]
    #         ave_ccnc_sizes = ave_ccnc_sizes[self.shift_factor:]
    #     else:  # -- if shift factor is negative
    #         # populate ccnc counts with 0s in the fronts
    #         ccnc_counts = hf.fill_zeros_to_begin(ccnc_counts, abs(self.shift_factor))
    #         ccnc_count_sums = hf.fill_zeros_to_begin(ccnc_count_sums, abs(self.shift_factor))
    #         ccnc_sample_flow = hf.fill_zeros_to_begin(ccnc_sample_flow, abs(self.shift_factor))
    #         t1s = hf.fill_zeros_to_begin(t1s, abs(self.shift_factor))
    #         t2s = hf.fill_zeros_to_begin(t2s, abs(self.shift_factor))
    #         t3s = hf.fill_zeros_to_begin(t3s, abs(self.shift_factor))
    #         super_sats = hf.fill_zeros_to_begin(super_sats, abs(self.shift_factor))
    #         ave_ccnc_sizes = hf.fill_zeros_to_begin(ave_ccnc_sizes, abs(self.shift_factor))
    #     # If the shifted data is not long enough to match duration, fill with zeros.
    #     ccnc_counts = hf.fill_zeros_to_end(ccnc_counts, self.duration)
    #     ccnc_count_sums = hf.fill_zeros_to_end(ccnc_count_sums, self.duration)
    #     ccnc_sample_flow = hf.fill_zeros_to_end(ccnc_sample_flow, self.duration)
    #     t1s = hf.fill_zeros_to_end(t1s, self.duration)
    #     t2s = hf.fill_zeros_to_end(t2s, self.duration)
    #     t3s = hf.fill_zeros_to_end(t3s, self.duration)
    #     super_sats = hf.fill_zeros_to_end(super_sats, self.duration)
    #     ave_ccnc_sizes = hf.fill_zeros_to_end(ave_ccnc_sizes, self.duration)
    #     # Update the objects values with the local calculations truncating to the length of duration
    #     self.processed_ccnc_counts = ccnc_counts[:self.duration]
    #     self.processed_ccnc_count_sums = ccnc_count_sums[:self.duration]
    #     self.processed_ccnc_sample_flow = ccnc_sample_flow[:self.duration]
    #     self.processed_T1s = t1s[:self.duration]
    #     self.processed_T2s = t2s[:self.duration]
    #     self.processed_T3s = t3s[:self.duration]
    #     self.processed_super_sats = super_sats[:self.duration]
    #     self.processed_ave_ccnc_sizes = ave_ccnc_sizes[:self.duration]
    #     self.true_super_sat = self.processed_super_sats[0]
    #     # Perform self test
    #     self.post_align_self_test()
    #     self.get_activation()
    #
    # def correct_charges(self):
    #     """
    #     Corrects the charges for the scan by resolving zeros to small values and correcting the charges via
    #     :class:`~fast_dp_calculator`
    #     """
    #     # scan is not usable, do nothing
    #     if not self.is_valid():
    #         return -1
    #     # Initiate some necessary variables
    #     ccnc = self.processed_ccnc_counts[:]
    #     smps = self.processed_smps_counts[:]
    #     ave_smps_dp = self.ave_smps_diameters[:]
    #     # Basic Processing
    #     ccnc = hf.resolve_zeros(ccnc)
    #     smps = hf.resolve_zeros(smps)
    #     ccnc = hf.resolve_small_ccnc_vals(ccnc)
    #     # Make copies of the lists
    #     prev_ccnc = np.copy(ccnc)
    #     prev_smps = np.copy(smps)
    #     corrected_ccnc = np.copy(ccnc)
    #     corrected_smps = np.copy(smps)
    #     # Correct the charges
    #     for i in range(const.NUM_OF_CHARGES_CORR):
    #         ave_smps_dp, smps, ccnc, corrected_smps, corrected_ccnc, prev_smps, prev_ccnc = \
    #             fast_dp_calculator.correct_charges(
    #                 ave_smps_dp, smps, ccnc, corrected_smps, corrected_ccnc, prev_smps, prev_ccnc)
    #     # Save the smps and ccnc data after charge correction to new variables
    #     self.corrected_smps_counts = corrected_smps
    #     self.corrected_ccnc_counts = corrected_ccnc
    #
    # def fit_sigmoids(self):
    #     """
    #     # REVIEW Documentation
    #     """
    #     # COMBAKL Sigmoid
    #     if not self.is_valid():
    #         return
    #     sigmoid_fit.get_all_fit_curves(self)
    #
    # def get_activation(self):
    #     """
    #     Calculates the activation percentage for each scan on the fly.
    #     Updates each time a new shift value is selected
    #
    #     :return: The activation percentage.  If an exception occurs, returns `"Unknown"`
    #     :rtype: str|int
    #     """
    #     # Sum of CCNC Uptime across all 20 bins  # TODO Fix
    #     ccnc_uptime = sum(self.processed_ccnc_count_sums[0:self.scan_up_time])
    #     # Sum of SMPS counts (Section 4) during Uptime
    #     smps_uptime = round(sum(self.processed_smps_counts[0:self.scan_up_time]) / self.counts_to_conc, 0)
    #     # Average Sample Flow (CCNC)
    #     mean_sample_flow = sum(self.processed_ccnc_sample_flow[0:self.scan_up_time])
    #     mean_sample_flow /= len((self.processed_ccnc_sample_flow[0:self.scan_up_time]))
    #
    #     if smps_uptime == 0 or sum(self.processed_ccnc_sample_flow[0:self.scan_up_time]) == 0:
    #         return "Unknown"
    #     else:
    #         try:
    #             return round(((ccnc_uptime / smps_uptime) * (self.cpc_sample_flow/(mean_sample_flow/1000))*100), 0)
    #         except Exception as e:
    #             logger.warning("Scan (" + str(self.index) + "):" + str(e))
    #             return "Unknown"
