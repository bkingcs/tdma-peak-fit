"""
This class handles most of the programs actions.
"""
# External Packages
import datetime as dt
from io import StringIO
import logging
import math
import numpy as np
import os
import pandas as pd
import pickle
import re
import time

# Internal Packages
# from algorithm import auto_shift
# import constants as const
# import helper_functions as hf
import scan

# Set logger for this module
logger = logging.getLogger("controller")


class Controller(object):
    """
    This class handles the functionalities of the program.

    Stores the following variables:

    - **scans**: A list of all scans
    - **counts_to_conc_conv**:
    - **data_files**:
    - **ccnc_data**: Data from the Cloud Condensation Nuclei Counter
    - **smps_data**: Data from the Scanning Mobility Particle Sizer
    - **experiment_date**: The date of experiment
    - **smooth_method**: The smoothing method
    - **base_shift_factor**: The base shift factor. Very useful for auto alignment.
    - **curr_scan_index**: Index of the current scan
    - **b_limits**: limits of the variable b
    - **asym_limits**: threshold for top assym
    - **stage**: The stage the program is in
    - **save_name**:
    - **project_folder**:
    - **sigma**:
    - **temp**:
    - **dd_1**:
    - **i_kappa_1**:
    - **dd_2**:
    - **i_kappa_2**:
    - **solubility**:
    - **kappa_excel**:
    - **valid_kappa_points**: whether kappa point is included in ave k calc (format is (dp,ss))
    - **alpha_pinene_dict**:
    - **kappa_calculate_dict**:

    .. attention:: This has unit tests

    :param MainView view: The main view of the program which is creating this controller.
    """
    # COMBAKL Sigmoid
    # COMBAKL Kappa
    def __init__(self, view):
        self.view = view
        # Variables consistent across scans
        # self.scan_up_time = None
        # self.scan_down_time = None
        # self.cpc_sample_flow = None
        # self.counts_to_conc_conv = None
        # # Variables set with set_attributes_default method
        self.scans = None
        # self.data_files = None
        # self.ccnc_data = None
        # self.smps_data = None
        # self.experiment_date = None
        # self.scan_duration = None
        # self.base_shift_factor = None
        # self.curr_scan_index = None
        # self.b_limits = None
        # self.asym_limits = None
        # self.stage = "init"
        # self.save_name = None
        # self.project_folder = None
        # variables for calculating kappa
        # QUESTION What can be constants?
        # self.sigma = 0.072
        # self.temp = 298.15
        # self.dd_1 = 280
        # self.i_kappa_1 = 0.00567
        # self.dd_2 = 100
        # self.i_kappa_2 = 0.6
        # self.solubility = 0.03
        # self.kappa_excel = None
        # Variables for calculating kappa set with set_attributes_default method
        #self.kappa_calculate_dict = None
        # self.alpha_pinene_dict = None
        # self.valid_kappa_points = None
        # self.set_attributes_default()
        # self.smooth_method = None  # TODO issues/41

    ####################
    # Resetting Values #
    ####################

    def set_attributes_default(self):
        """
        Sets a subset of the controller variables to their original default values.  This method runs when the
        controller is first initlized and when a new project is started.

        .. attention:: This has unit tests
        """
        # DOCQUESTION What can be constants?
        self.scans = []
        self.counts_to_conc_conv = 0
        self.cpc_sample_flow = 0.5
        self.data_files = None
        self.ccnc_data = None
        self.smps_data = None
        self.experiment_date = None
        self.base_shift_factor = 0
        self.curr_scan_index = 0
        self.b_limits = [0.5, 1.5]
        self.asym_limits = [0.75, 1.5]
        self.stage = "init"
        self.save_name = None
        #self.kappa_calculate_dict = {}
        self.alpha_pinene_dict = {}
        self.valid_kappa_points = {}

    ###################
    # Processing Data #
    ###################

    def start(self, data_files):
        """
        Starts a new project by processing the following methods:

        - :class:`~controller.Controller.parse_files`
        - :class:`~controller.Controller.create_scans`
        - :class:`~controller.Controller.get_normalized_concentration`
        - :class:`~controller.Controller.get_smps_counts`
        - :class:`~controller.Controller.get_ccnc_counts`
        - :class:`~controller.Controller.do_basic_trans`
        - :class:`~controller.Controller.pre_align_sanity_check`

        :param list[str] data_files: The full path names of the filed selected in the new project from files dialog box
        """
        self.project_folder = os.path.dirname(os.path.dirname(data_files[0]))
        # reset the attributes
        self.set_attributes_default()
        # got to reset the view first
        self.view.reset_view()
        # take in new data and rock on!
        self.data_files = data_files  # DOCQUESTION Allow adding additional files later?
        self.view.init_progress_bar("Reading in SMPS and CCNC data files")
        # TODO issues/47 So many magic numbers in the following functions.  Find what can be constants.
        self.parse_files()
        self.view.update_progress_bar(5)
        self.create_scans()
        self.view.update_progress_bar(15)
        self.get_normalized_concentration()
        self.view.update_progress_bar(35)
        self.get_smps_counts()
        self.view.update_progress_bar(65)
        self.get_ccnc_counts()
        self.view.update_progress_bar(85)
        self.do_basic_trans()
        self.view.update_progress_bar(95)
        self.pre_align_sanity_check()
        self.view.update_progress_bar(100)
        self.view.close_progress_bar()
        # Update the experiment info in the view
        self.view.update_experiment_info()
        self.auto_align_scans()
        self.stage = "align"
        # update the menu
        self.view.set_menu_bar_by_stage()

    def auto_align_scans(self):
        """
        # REVIEW Documentation

        :return:
        :rtype:
        """
        self.view.init_progress_bar("Aligning SMPS and CCNC data...")
        # Find the median shift factor of unadjusted shifts to get a general idea of the shift
        shift_factors = []
        for i in range(len(self.scans)):
            self.view.update_progress_bar(100 * (i + 1) // len(self.scans) // 2)
            a_scan = self.scans[i]
            shift_factors.append(auto_shift.get_auto_shift(a_scan.raw_smps_counts,
                                                           a_scan.raw_ccnc_counts,
                                                           a_scan.scan_up_time, 0)[0])
        median_shift = sorted(shift_factors)[(len(shift_factors) + 1) // 2]

        # Using the approximate median shift factor, find actual shift values.
        for i in range(len(self.scans)):
            self.view.update_progress_bar(50 + (100 * (i + 1) // len(self.scans) // 2))
            a_scan = self.scans[i]
            shift_factor, err_msg = auto_shift.get_auto_shift(a_scan.raw_smps_counts,
                                                              a_scan.raw_ccnc_counts,
                                                              a_scan.scan_up_time,
                                                              median_shift)
            for index, value in enumerate(err_msg):
                if index == 0:
                    logger.warning("get_auto_shift error on scan: " + str(i))
                logger.warning("    (%d) %s" % (index, value))
            self.scans[i].set_shift_factor(shift_factor)
            self.scans[i].generate_processed_data()
        self.view.close_progress_bar()
        self.post_align_sanity_check()
        self.switch_to_scan(0)

    # def export_scans(self, filename):
    #     """
    #     Exports all scans to excel.  Used ONLY For debugging.
    #
    #     :param str filename: The name to save the file as.  Can include directory structure,
    #                          be relative to cwd or absolute.
    #     """
    #     import export_data
    #     export_data.export_scans(self.scans, filename)

    # def correct_charges(self):
    #     """
    #     Correct the charges of all the scans.
    #     """
    #     # QUESTION What does this mean? - Document the answer
    #     # Correcting charges
    #     self.view.init_progress_bar("Correcting charges...")
    #     for i in range(len(self.scans)):
    #         self.view.update_progress_bar(100 * (i + 1) // len(self.scans))
    #         self.scans[i].correct_charges()
    #     self.view.close_progress_bar()
    #     self.view.show_sigmoid_docker()
    #     self.stage = "sigmoid"
    #     self.switch_to_scan(0)


    # def cal_kappa(self):
    #     """
    #     # REVIEW Documentation
    #     """
    #     # COMBAKL Kappa
    #     self.calculate_all_kappa_values()
    #     self.calculate_average_kappa_values()
    #     self.stage = "kappa"
    #     self.view.switch_to_kappa_view()

    # def calculate_all_kappa_values(self):
    #     """
    #     # REVIEW Documentation
    #     """
    #     # COMBAKL Kappa
    #     if self.kappa_excel is None:
    #         self.kappa_excel = pd.read_csv(StringIO(ProgramCode.data.kCal.csv_codes), header=None)
    #     lookup = self.kappa_excel
    #     a_param = 0.00000869251 * self.sigma / self.temp
    #     # asc = (exp(sqrt(4 * a_param ** 3 / (27 * self.i_kappa_1 * (self.dd_1 * 0.000000001) ** 3))) - 1) * 100
    #     # Calculate each kappa
    #     ss_and_dps = []
    #     for i in range(len(self.scans)):
    #         a_scan = self.scans[i]
    #         if not a_scan.is_valid() or a_scan.true_super_sat is None:
    #             continue
    #         ss = a_scan.true_super_sat
    #         activation = a_scan.get_activation()
    #         for j in range(len(a_scan.dp50)):
    #             dp_50 = a_scan.dp50[j]
    #             # REVIEW kset Create ss_and_dps
    #             ss_and_dps.append([i, ss, dp_50, activation])
    #     for i in range(len(ss_and_dps)):
    #         # REVIEW kset Create use ss_and_dps
    #         scan_index = float(ss_and_dps[i][0])
    #         ss = float(ss_and_dps[i][1])
    #         dp_50 = float(ss_and_dps[i][2])
    #         activation = float(ss_and_dps[i][3])
    #         row_index = int(math.floor(dp_50 - 9))
    #         match_row = list(lookup.iloc[row_index][1:])
    #         value_row = list(lookup.iloc[0][1:])
    #         a = hf.get_correct_num(match_row, ss)
    #         c_index = a[1]
    #         a = a[0]
    #         if c_index != (len(match_row) - 1):
    #             b = match_row[c_index + 1]
    #             c = value_row[c_index]
    #             d = value_row[c_index + 1]
    #         else:
    #             c = value_row[c_index]
    #             b = 0
    #             d = 0
    #         apparent_kappa = (ss - (a - (a - b) / (c - d) * c)) / ((a - b) / (c - d))
    #         analytic_kappa = (4 * a_param ** 3) / (27 * (dp_50 * 0.000000001) ** 3 * math.log(ss / 100 + 1) ** 2)
    #         deviation_percentage = (apparent_kappa - analytic_kappa) / apparent_kappa * 100
    #         if ss in list(self.kappa_calculate_dict.keys()):
    #             # REVIEW kset set kappa dict values, key = ss
    #             self.kappa_calculate_dict[ss].append([scan_index, dp_50, apparent_kappa, activation,
    #                                                   analytic_kappa, deviation_percentage])
    #         else:
    #             # REVIEW kset set kappa dict values, key = ss
    #             self.kappa_calculate_dict[ss] = ([[scan_index, dp_50, apparent_kappa, activation,
    #                                                analytic_kappa, deviation_percentage]])
    #         # REVIEW kset set value kappa points key, value = true
    #         self.valid_kappa_points[(scan_index, dp_50, ss, activation)] = True
    #
    # def calculate_average_kappa_values(self):
    #     """
    #     # REVIEW Documentation
    #     """
    #     # COMBAKL Kappa
    #     # Calculate the kappa values for each supersaturation percentage. The values are average of all scans with the
    #     # same supersaturation        self.alpha_pinene_dict = {}
    #     # REVIEW kset use kappa dict
    #     for a_key in list(self.kappa_calculate_dict.keys()):
    #         scan_list_at_ss = self.kappa_calculate_dict[a_key]
    #         temp_dp50_list = []
    #         dp_50s = []
    #         apparent_kappas = []
    #         analytical_kappas = []
    #         mean_of_stds = []
    #         for aSS in scan_list_at_ss:
    #             # scan_index, dp_50, apparent_kappa, activation, analytic_kappa, deviation_percentage
    #             dp_50s.append((aSS[0], aSS[1], aSS[3]))
    #             # REVIEW kset use valid kappa points
    #             if self.valid_kappa_points[(aSS[0], aSS[1], a_key, aSS[3])]:
    #                 temp_dp50_list.append(aSS[1])
    #                 apparent_kappas.append(aSS[2])
    #                 analytical_kappas.append(aSS[4])
    #                 mean_of_stds.append(aSS[5])
    #         mean_dp = np.average(temp_dp50_list)
    #         std_dp = np.std(temp_dp50_list)
    #         mean_app = np.average(apparent_kappas)
    #         std_app = np.std(apparent_kappas)
    #         mean_ana = np.average(analytical_kappas)
    #         std_ana = np.std(analytical_kappas)
    #         mean_dev = np.average(mean_of_stds)
    #         dev_mean = (mean_app - mean_ana) / mean_app * 100
    #         self.alpha_pinene_dict[a_key] = (
    #             mean_dp, std_dp, mean_app, std_app, mean_ana, std_ana, mean_dev, dev_mean, dp_50s)

    ############################
    # New Project File Parsing #
    ############################

    def parse_files(self):
        """
        Takes the list of data_files stored in the controller and determines:

        - self.experiment_date from the first ccnc file record
        - ccnc_data from the csv file(s)
        - smps_data from the txt file
        - Sets the counts_to_conc_conv value by finding the CPC Sample Flow(lpm) value
        from the SMPS file and performs the following conversion to convert the liter per
        minute measure into a second per CC value.

        (1 minute / "CPC Sample Flow" L)  *  (60 seconds / 1 minute)  *  (1 L / 1000 cc)

        """
        ccnc_csv_files = []  # Should be hourly files  # TODO issues/25 Add error handling
        smps_txt_files = []  # Should be one file  # TODO issues/25 Add error handling
        # Acquire the smps and ccnc files from the input files
        for a_file in self.data_files:
            if a_file.lower().endswith('.csv'):
                ccnc_csv_files.append(a_file)
            elif a_file.lower().endswith('.txt'):
                smps_txt_files.append(a_file)
        # Stringify each item in the list
        ccnc_csv_files = [str(x) for x in ccnc_csv_files]
        smps_txt_files = [str(x) for x in smps_txt_files]
        # Turn smps to a str instead of a list - Assumes only one file
        smps_txt_files = smps_txt_files[0]
        self.experiment_date, self.ccnc_data = hf.process_csv_files(ccnc_csv_files)
        self.smps_data = hf.process_tab_sep_files(smps_txt_files)

        # Obtain data that is consistant across scans
        # Determine scan duration which is the sum of the scan up time and the retrace time.
        # -- Find first scan up time  # DOCQUESTION Assume ALWAYS the same?
        for i in range(len(self.smps_data)):
            if ''.join(self.smps_data[i][0].split()).lower() == "scanuptime(s)":
                self.scan_up_time = int(self.smps_data[i][1])
                self.scan_down_time = int(self.smps_data[i + 1][1])  # this is the retrace time
                self.cpc_sample_flow = float(self.smps_data[i + 8][1])
                break
        # DOCQUESTION Which leads to always assuming this is same
        self.scan_duration = self.scan_up_time + self.scan_down_time
        self.counts_to_conc_conv = (1.0/self.cpc_sample_flow) * (3/50)

    def create_scans(self):
        """
        Creates the scans objects and updates via the following scan methods:

        - :class:`~scan.Scan.set_start_time` From the SMPS file
        - :class:`~scan.Scan.set_end_time` Start time + Duration
        - :class:`~scan.Scan.set_up_time` From the SMPS file
        - :class:`~scan.Scan.set_down_time` From the SMPS file (retrace time)
        - :class:`~scan.Scan.set_duration` Scan up time + Scan down time
        - :class:`~scan.Scan.set_counts_2_conc` As calculated earlier
        - :class:`~scan.Scan.set_cpc_sample_flow` from the SMPS file
        """
        # Get a list of all the start times
        scan_start_times = self.smps_data[0]  # TODO issues/4 Affected by the changed to storing the AIM Scan #
        # For each scan time
        for i in range(len(scan_start_times)):
            # Create a scan object
            a_scan = scan.Scan(i)
            # Add it to the scan list
            self.scans.append(a_scan)
            # Create time objects
            start_time = dt.datetime.strptime(scan_start_times[i], "%H:%M:%S")
            end_time = start_time + dt.timedelta(seconds=self.scan_duration)
            # Set Scan values
            a_scan.set_start_time(start_time)
            a_scan.set_end_time(end_time)
            a_scan.set_up_time(self.scan_up_time)
            a_scan.set_down_time(self.scan_down_time)
            a_scan.set_duration(self.scan_duration)
            a_scan.set_counts_2_conc(self.counts_to_conc_conv)
            a_scan.set_cpc_sample_flow(self.cpc_sample_flow)

    def do_basic_trans(self):
        """
        Perform basic transformation before aligning the smps and ccnc data.
        See scan's method :class:`~scan.Scan.do_basic_trans` for more details.
        """
        for i in range(len(self.scans)):
            self.scans[i].do_basic_trans()

    def pre_align_sanity_check(self):
        """
        Completes the sanity check which checks:

        - Length of the smps data sync with duration via :class:`~scan.Scan.pre_align_self_test`
        - The distribution of a scan with the next two
        """
        # Perform self test for each scan
        for i in range(len(self.scans)):
            self.scans[i].pre_align_self_test()
        # DOCQUESTION Cross validation. Basically compare the distribution of a scan with the next two
        # We know that only the first few distributions have weird data, so once it becomes right, we stop
        for i in range(len(self.scans) - 2):
            # if the scan is invalid, we skip to the next one
            if not self.scans[i].is_valid():
                continue
            # if a scan has a different dist from the next one or the one after that
            if not self.scans[i].compare_smps(self.scans[i + 1]) or not self.scans[i].compare_smps(self.scans[i + 2]):
                self.scans[i].set_status(0)
                self.scans[i].set_status_code(3)  # RESEARCH 3 Status Code
            else:
                break

    def post_align_sanity_check(self):
        """
        Currently an empty method.  May preform additional functions in the future.
        """
        # TODO: outliers detection
        # TODO: fix all wrong shift factors
        pass

    ##################################
    # Data Manipulation by the user  #
    ##################################

    # def set_kappa_point_state(self, ss, dp, state):
    #     """
    #     # REVIEW Documentation
    #
    #     :param ss:
    #     :type ss:
    #     :param dp:
    #     :type dp:
    #     :param state:
    #     :type state:
    #     """
    #     # COMBAKL Kappa
    #     self.valid_kappa_points[(dp, ss)] = state
    #     self.calculate_average_kappa_values()
    #     self.view.update_kappa_graph()

    #################
    # Updating view #
    #################

    def set_scan_index(self, new_index):
        """
        Sets the current index in the controller

        :param int new_index: The new index
        """
        self.curr_scan_index = new_index
        # RESEARCH Shouldn't this update the view automatically?

    def switch_to_scan(self, index):
        """
        Switches the controller to activate a specific scan and updates the view appropriately

        :param int index: The index of the scan in the `self.scans[]` list to activate
        """
        self.curr_scan_index = index
        self.view.update_scan_info_and_graphs()
        self.view.set_menu_bar_by_stage()

    def preview_scans(self, timer):
        """
        Cycles through the scan starting from zero and then returns to the scan on when triggered

        :param Union[int,float] timer:  The length of time between scans.  The actual sleep time requested will be this
                                 value minus 0.5 as there is an inherent delay when switching
        """
        # because there is an inherent delay time when switch
        timer = max(0, timer - 0.5)
        # Store current index so that view can be restored after
        actual_curr_scan_index = self.curr_scan_index
        # Cycle through all scans
        self.view.init_progress_bar("Previewing all scans...")
        for i in range(len(self.scans)):
            self.view.update_progress_bar(100 * i // len(self.scans))
            self.switch_to_scan(i)
            if self.view.progress_dialog.wasCanceled():
                break
            time.sleep(timer)
        # Return things as it were  # QUESTION More useful if it didn't break if cancelled mid scan
        self.switch_to_scan(actual_curr_scan_index)
        # Short sleep to allow the switch to finish before closing the progress bar  # RESEARCH better way
        time.sleep(0.1)
        self.view.close_progress_bar()

    ##############
    # Get values #
    ##############

    # def get_project_name(self):
    #     """
    #     Takes the absolute project folder path and returns the last folder as the project name.
    #
    #     :return: The parent folder name
    #     :rtype: str
    #     """
    #     return os.path.basename(self.project_folder)

    ##############
    # Set values #
    ##############

    # def set_save_name(self, name):
    #     """
    #     Sets the savename of the file
    #
    #     :param str name: The name to save the file as
    #     """
    #     self.save_name = name

    ## Create Advanced Settings

    # def set_sigma(self, sigma):
    #     """
    #     # REVIEW Documentation
    #
    #     :param sigma:
    #     :type sigma:
    #     """
    #     # COMBAKL Kappa
    #     self.sigma = sigma
    #
    # def set_temp(self, temp):
    #     """
    #     # REVIEW Documentation
    #
    #     :param temp:
    #     :type temp:
    #     """
    #     # COMBAKL Kappa
    #     self.temp = temp
    #
    # def set_dd_1(self, dd_1):
    #     """
    #     # REVIEW Documentation
    #
    #     :param dd_1:
    #     :type dd_1:
    #     """
    #     # COMBAKL Kappa
    #     self.dd_1 = dd_1
    #
    # def set_dd_2(self, dd_2):
    #     """
    #     # REVIEW Documentation
    #
    #     :param dd_2:
    #     :type dd_2:
    #     """
    #     # COMBAKL Kappa
    #     self.dd_2 = dd_2
    #
    # def set_i_kappa_1(self, value):
    #     """
    #     # REVIEW Documentation
    #
    #     :param value:
    #     :type value:
    #     """
    #     # COMBAKL Kappa
    #     self.i_kappa_1 = value
    #
    # def set_i_kappa_2(self, value):
    #     """
    #     # REVIEW Documentation
    #
    #     :param value:
    #     :type value:
    #     """
    #     # COMBAKL Kappa
    #     self.i_kappa_2 = value
    #
    # def set_solubility(self, value):
    #     """
    #     # REVIEW Documentation
    #
    #     :param value:
    #     :type value:
    #     """
    #     # COMBAKL Kappa
    #     self.solubility = value

    #########################
    # Project Manipulations #
    #########################

    # def save_project(self):
    #     """
    #     Stores the following variables.
    #
    #     - self.scans
    #     - self.counts_to_conc_conv
    #     - self.data_files
    #     - self.ccnc_data
    #     - self.smps_data
    #     - self.experiment_date
    #     - self.base_shift_factor
    #     - self.b_limits
    #     - self.asym_limits
    #     - self.kappa_calculate_dict
    #     - self.alpha_pinene_dict
    #     - self.stage
    #     - self.valid_kappa_points
    #     - self.save_name
    #     """
    #     # TODO issues/41 Fix to remove smooth_method
    #     if self.save_name is None:
    #         self.view.save_project_as()
    #     else:
    #         to_save = (self.scans, self.counts_to_conc_conv, self.data_files, self.ccnc_data, self.smps_data,
    #                    self.experiment_date, self.smooth_method, self.base_shift_factor, self.b_limits,
    #                    self.asym_limits, self.kappa_calculate_dict, self.alpha_pinene_dict, self.stage,
    #                    self.valid_kappa_points,
    #                    self.save_name)
    #         with open(self.save_name, 'wb') as handle:
    #             pickle.dump(to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #
    # def load_project(self, project_file):
    #     """
    #     Begins a project with new project files
    #
    #     :param unicode project_file: The project file to reopen
    #     """
    #     # TODO issues/41 Fix to remove smooth_method
    #     # RESEARCH Any other variables that need to be handled, cleared, etc?
    #     # Get project folder
    #     self.project_folder = os.path.dirname(project_file)
    #     try:
    #         with open(project_file, 'rb') as handle:
    #             (self.scans, self.counts_to_conc_conv, self.data_files, self.ccnc_data, self.smps_data,
    #              self.experiment_date, self.smooth_method, self.base_shift_factor, self.b_limits,
    #              self.asym_limits, self.kappa_calculate_dict, self.alpha_pinene_dict, self.stage,
    #              self.valid_kappa_points,
    #              self.save_name) = pickle.load(handle)
    #     except Exception as e:
    #         logger.warning("Old project/run file attempted to load (%s)" % e)
    #         self.view.show_error_message("old project file")
    #         return
    #     # except TypeError as e:
    #     #     if str(e) == "__init__() takes exactly 2 arguments (1 given)":
    #     #         with open(project_file, 'rb') as handle:
    #     #             (self.scans, self.counts_to_conc_conv, self.data_files, self.ccnc_data, self.smps_data,
    #     #              self.experiment_date, self.smooth_method, self.base_shift_factor, self.b_limits,
    #     #              self.asym_limits, self.kappa_calculate_dict, self.alpha_pinene_dict, self.stage,
    #     #              self.valid_kappa_points,
    #     #              self.save_name) = hf.CustomUnpickler(handle).load()
    #     # except ImportError as e:
    #     #     if str(e) == "No module named Scan":
    #     #         logger.warn("run import but no module named Scan - CustomUnpickler")
    #     #         with open(project_file, 'rb') as handle:
    #     #             (self.scans, self.counts_to_conc_conv, self.data_files, self.ccnc_data, self.smps_data,
    #     #              self.experiment_date, self.smooth_method, self.base_shift_factor, self.b_limits,
    #     #              self.asym_limits, self.kappa_calculate_dict, self.alpha_pinene_dict, self.stage,
    #     #              self.valid_kappa_points,
    #     #              self.save_name) = hf.CustomUnpickler(handle).load()
    #
    #     # Set up the View
    #     self.view.reset_view()
    #     self.view.update_experiment_info()
    #     self.view.set_menu_bar_by_stage()
    #     self.switch_to_scan(0)
    #     # if got to kappa, go straight to the kappa view
    #     if self.stage == "kappa":
    #         self.view.switch_to_kappa_view()
    #         return
    #     if self.stage == "sigmoid":
    #         self.view.show_sigmoid_docker()
    #     # QUESTION Show first valid scan or first scan?
    #     self.switch_to_scan(0)
    #
    # def export_project_data(self, export_filename):
    #     """
    #     Export the Kappa data to csv.
    #
    #     :param str export_filename: The file name to export the file to
    #     """
    #     # TODO issues/20 issues/21 issues/22 issues/11
    #     data_to_export = []
    #     # REVIEW kset use kappa dist
    #     for a_key in list(self.kappa_calculate_dict.keys()):
    #         a_scan = self.kappa_calculate_dict[a_key]
    #         for aSS in a_scan:
    #             # REVIEW kset use valid_kappa_points
    #             if self.valid_kappa_points[(aSS[0], aSS[1], a_key, aSS[3])]:
    #                 a_row = [a_key] + aSS[:-2] + ["Included point"]
    #             else:
    #                 a_row = [a_key] + aSS[:-2] + ["Excluded point"]
    #             data_to_export.append(a_row)
    #     df = pd.DataFrame(np.asarray(data_to_export),
    #                       columns=["Supersaturation(%)", "Scan Index", "dp(nm)",
    #                                "K/app", "% activation", "Status"])
    #     df.to_csv(export_filename, index=False)
    #     self.view.show_information_message(title="Export Data", text="Export to " + export_filename + " successful!")
