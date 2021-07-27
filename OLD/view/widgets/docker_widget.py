"""
Creates the various widgets that display in the docker section of the display
"""
# External Packages
import datetime as dt
import numpy as np
import PySide2.QtCore as Qc
import PySide2.QtGui as Qg
import PySide2.QtWidgets as Qw

# Internal Packages
import OLD.view.widgets.modal_dialogs as c_modal_dialogs
import OLD.view.widgets.widget as c_widget


class DockerScanInformation(Qw.QFrame):
    """
    Creates the docker widget (docker = left pane) that displays the scan information.

    :param Controller controller: The controller for the current program
    """
    def __init__(self, controller):
        super(self.__class__, self).__init__()
        self.controller = controller
        # set up the layout
        form_layout = Qw.QFormLayout()
        self.setContentsMargins(-10, -10, 0, -10)
        form_layout.setContentsMargins(30, 20, 20, 0)
        self.setAutoFillBackground(True)
        palette = Qg.QPalette()
        palette.setColor(Qg.QPalette.Background, Qc.Qt.white)
        self.setPalette(palette)
        self.setFrameShape(Qw.QFrame.StyledPanel)
        self.setFrameShadow(Qw.QFrame.Plain)
        ########################################
        # Top Section - Experiment Information
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Experiment Information"))
        # -- add date
        self.experiment_date = Qw.QLabel("-")
        self.experiment_date.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Date (m/d/y)", self.experiment_date)
        # -- add scan up time
        self.scan_up_time = Qw.QLabel("-")
        self.scan_up_time.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan Up Time (s)", self.scan_up_time)  # DOCQUESTION Convert to complete sentence
        # -- add retrace time
        self.retrace_time = Qw.QLabel("-")
        self.retrace_time.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Retrace Time (s)", self.retrace_time)
        ########################################
        # Middle Section - Update Scan
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Update Scan"))
        # -- add the scan selector
        self.scan_selector = c_widget.ArrowSpinBox(forward=True)
        self.scan_selector.set_callback(self.scan_index_changed)
        self.scan_selector.set_range(0, 0)
        form_layout.addRow("Scan number", self.scan_selector)
        # -- add the shift selector
        self.shift_selector = c_widget.ArrowSpinBox(forward=True)
        self.shift_selector.set_callback(self.shift_factor_changed)
        self.shift_selector.set_range(0, 0)
        form_layout.addRow("Shift (s)", self.shift_selector)
        # -- add the buttons
        # ---- add show data action
        self.show_data_button = Qw.QPushButton("Show Data")
        # noinspection PyUnresolvedReferences
        self.show_data_button.clicked.connect(self.show_data)  # RESEARCH connect unresolved ref
        # ---- add the enable/disable button
        self.enable_disable_button = Qw.QPushButton("Disable scan")
        # noinspection PyUnresolvedReferences
        self.enable_disable_button.clicked.connect(self.set_scan_enable_status)  # RESEARCH connect unresolved ref
        # form_layout.addRow(self.show_data_button, self.enable_disable_button)  # RESEARCH Put buttons on same line
        form_layout.addRow(self.enable_disable_button)
        form_layout.addRow(self.show_data_button)
        ########################################
        # Bottom Section - Scan Details
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("First DMA"))
        # -- add the low voltage_lineedit
        self.low_voltage = Qw.QLabel("-")
        self.low_voltage.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Low Voltage ", self.low_voltage)
        # -- add the high voltage_lineedit
        self.status_flag = Qw.QLabel("-")
        self.status_flag.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("High Voltage", self.status_flag)
        # -- add the status flag
        self.status_flag = Qw.QLabel("-")
        self.status_flag.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Status Flag", self.status_flag)
        # -- add the sheath flow
        self.sheath_flow = Qw.QLabel("-")
        self.sheath_flow.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Sheath Flow", self.sheath_flow)
        # -- add the aerosol flow
        self.aerosol_flow = Qw.QLabel("-")
        self.aerosol_flow.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Aerosol Flow", self.aerosol_flow)
        ## -- add the status of the scan
        # form_layout.addRow("Additional Info", None)
        # self.additional_information = Qw.QTextEdit("Welcome to Chemics!")
        # self.additional_information.setReadOnly(True)
        # self.additional_information.setAlignment(Qc.Qt.AlignLeft)
        # form_layout.addRow(self.additional_information)
        # set the layout
        self.setLayout(form_layout)

    def update_scan_info(self):
        """
        Updates the scan detail section of the Scan Information widget
        """
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        # Update the Update Scan section
        self.scan_selector.set_value(self.controller.curr_scan_index)
        self.shift_selector.set_value(curr_scan.shift_factor)
        # Update the Scan Details section
        start_time = dt.date.strftime(curr_scan.start_time, "%H:%M:%S")
        end_time = dt.date.strftime(curr_scan.end_time, "%H:%M:%S")
        scan_time = start_time + " - " + end_time
        self.scan_time.setText(scan_time)
        if not hasattr(curr_scan, "super_sat_label") or curr_scan.super_sat_label is None:
            curr_scan.super_sat_label = ', '.join(map(str, np.unique(curr_scan.processed_super_sats)))
        self.retrace_time.setText(curr_scan.super_sat_label)
        self.retrace_time.mousePressEvent = self.update_supersaturation
        self.low_voltage.setText(str(curr_scan.get_activation()))
        if curr_scan.is_valid():
            self.status_flag.setText("VALID")
            self.status_flag.setStyleSheet("QWidget { background-color:None}")
            self.additional_information.setText("The scan shows no problem.")
            self.enable_disable_button.setText("Disable scan")
        else:
            self.status_flag.setText("INVALID")
            self.status_flag.setStyleSheet("QWidget { color: white; background-color:red}")
            self.additional_information.setText(curr_scan.get_status_code_descript())
            self.enable_disable_button.setText("Enable scan")

    def update_experiment_info(self):
        """
        Updates the experiment information section of the Scan Information widget
        """
        # Get the number scans
        num_scan = len(self.controller.scans)
        # Update the values
        self.experiment_date.setText(self.controller.experiment_date)
        self.scan_duration.setText(str(self.controller.scan_duration))
        self.retrace_time.setText(str(len(self.controller.scans)))
        self.scan_up_time.setText(str(self.controller.counts_to_conc_conv))
        # Set the Arrow Box ranges
        # DOCQUESTION Possible shift range correct?  [If dur=135, possible is -68-67]
        self.shift_selector.set_range(-self.controller.scans[0].duration // 2, self.controller.scans[0].duration // 2)
        self.scan_selector.set_range(0, num_scan - 1)  # TODO issues/5

    def scan_index_changed(self, new_scan_index):
        """
        Callback function set when a new scan is selected on the Scan Information docker widget.  It:

        - Sets the current scan index in the controller (:class:`~controller.Controller.set_scan_index`)
        - Switches to the new scan via the controller (:class:`~controller.Controller.switch_to_scan`)

        :param int new_scan_index: The new index to set in the the controller and view.
        """
        self.controller.set_scan_index(new_scan_index)  # RESEARCH shouldn't set index auto switch scan?  Why not?
        self.controller.switch_to_scan(new_scan_index)  # If so, this line is redundent

    def shift_factor_changed(self, new_shift_index):
        """
        Callback function set when the shift factor is changed on the Scan Information docker widget.  It:

        - Sets the shift factor on the scan (:class:`~scan.Scan.set_shift_factor`)
        - Reprocesses the data (:class:`~scan.Scan.generate_processed_data`)
        - Reloads the current scan into the display (:class:`~controller.Controller.switch_to_scan`)

        :param int new_shift_index: The new shift value to set in the controller
        """
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        curr_scan.set_shift_factor(new_shift_index)        # RESEARCH shouldn't set index auto update display?  Why not?
        curr_scan.generate_processed_data()                # If so, this may be redundent
        self.controller.switch_to_scan(self.controller.curr_scan_index)    # As well as this line

    def set_scan_enable_status(self):
        """
        Toggles the enabled status of a scan.  Updates the scan values and the scan information display.
        """
        # TODO issues/45 Update code when reworked scan status code
        if len(self.controller.scans) != 0:
            curr_scan = self.controller.scans[self.controller.curr_scan_index]
            # Scan is originally marked good
            if curr_scan.status == 1:
                curr_scan.status = 0
                curr_scan.set_status_code(9)
            else:
                curr_scan.status = 1
                curr_scan.set_status_code(0)
            if curr_scan.is_valid():
                self.status_flag.setText("VALID")
                self.status_flag.setStyleSheet("QWidget { background-color:None}")
                self.additional_information.setText(curr_scan.get_status_code_descript())
                self.enable_disable_button.setText("Disable this scan")
            else:
                self.status_flag.setText("INVALID")
                self.status_flag.setStyleSheet("QWidget { color: white; background-color:red}")
                self.additional_information.setText(curr_scan.get_status_code_descript())
                self.enable_disable_button.setText("Enable this scan")
            self.controller.view.ratio_dp_graph.update_graph(curr_scan)

    def show_data(self):
        """
        Shows the dialog box which displays the scan's data to the user
        (:class:`~widgets.modal_dialogs.ScanDataDialog`)
        """
        if len(self.controller.scans) != 0:
            a_scan = self.controller.scans[self.controller.curr_scan_index]
            dialog = c_modal_dialogs.ScanDataDialog(a_scan)
            dialog.exec_()

    # noinspection PyUnusedLocal
    def update_supersaturation(self, event):
        """
        # REVIEW Documentation
        :return:
        :rtype:
        """
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        curr_ss = curr_scan.true_super_sat
        if curr_ss is None:
            curr_ss = curr_scan.raw_super_sats[0]
        if curr_ss is None:
            curr_ss = 0.0
        # noinspection PyCallByClass
        ss = Qw.QInputDialog.getDouble(self, "Update Supersaturation", "What is the correct supersaturation level",
                                       value=float(curr_ss), decimals=2)
        if ss[1]:
            curr_scan.true_super_sat = float(ss[0])
            curr_scan.super_sat_label = str(ss[0])
            self.retrace_time.setText(curr_scan.super_sat_label)


class DockerSigmoidWidget(Qw.QFrame):
    """
    Creates the docker widget that appears on the left that shows scan information

    :param Controller controller: The Controller object that controls the program
    """
    def __init__(self, controller):
        # TODO issues/17 Add Scan information section
        # TODO issues/10 Add toggle to show or hide invalid scans
        super(self.__class__, self).__init__()
        self.controller = controller
        self.num_sigmoid_lines = 0
        self.dp_widgets = []
        self.curr_scan_index = self.controller.curr_scan_index
        # set up the layout
        form_layout = Qw.QFormLayout()
        self.setContentsMargins(-10, -10, 0, -10)
        form_layout.setContentsMargins(30, 20, 20, 0)
        self.setAutoFillBackground(True)
        palette = Qg.QPalette()
        palette.setColor(Qg.QPalette.Background, Qc.Qt.white)
        self.setPalette(palette)
        self.setFrameShape(Qw.QFrame.StyledPanel)
        self.setFrameShadow(Qw.QFrame.Plain)
        ########################################
        # Top Section - Experiment Information
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Experiment Information"))
        # -- add date
        self.experiment_date = Qw.QLabel("-")
        self.experiment_date.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Date (m/d/y)", self.experiment_date)
        # -- add the scan time
        self.scan_time = Qw.QLabel("-")
        self.scan_time.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan Time (h:m:s)", self.scan_time)
        # -- add the supersaturation indicator
        self.supersaturation = Qw.QLabel("-")
        self.supersaturation.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Supersaturation (%)", self.supersaturation)
        ########################################
        # Middle Section - Update Scan
        # -- add a title
        form_layout.addRow(c_widget.TitleHLine("Update Sigmoid Parameters"))
        # Layout sigmoid parameters section
        # -- add the scan selector
        self.scan_selector = c_widget.ArrowSpinBox(forward=True)
        self.scan_selector.set_callback(self.scan_index_changed)
        form_layout.addRow("Scan number", self.scan_selector)
        # -- add the status of the scan
        self.scan_status = Qw.QLabel("-")
        self.scan_status.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Scan Status", self.scan_status)
        # -- add the status of the sigmoid
        self.sigmoid_status = Qw.QLabel("-")
        self.sigmoid_status.setAlignment(Qc.Qt.AlignRight)
        form_layout.addRow("Sigmoid Fit Status", self.sigmoid_status)
        # -- add the params area
        self.sigmoid_line_spinbox = c_widget.ArrowSpinBox(forward=True)
        form_layout.addRow("Number of sigmoid lines", self.sigmoid_line_spinbox)
        self.sigmoid_line_spinbox.set_callback(self.num_sigmoids_changed)
        # -- Add the apply button
        button_boxes = Qw.QDialogButtonBox()
        self.apply_button = button_boxes.addButton("Apply", Qw.QDialogButtonBox.ApplyRole)
        self.apply_button.clicked.connect(self.apply_sigmoid_params)  # RESEARCH why no connect unresolved ref
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    def num_sigmoids_changed(self, new_sigmoid_number):
        """
        Adds or removes Parameter Set widgets

        :param int new_sigmoid_number:  The new number of sigmoid lines
        """
        if new_sigmoid_number > self.num_sigmoid_lines:
            for i in range(new_sigmoid_number - self.num_sigmoid_lines):
                self.add_params_group_box()
        else:
            for i in range(self.num_sigmoid_lines - new_sigmoid_number):
                self.rem_params_group_box()

    def scan_index_changed(self, new_scan_index):
        """
        Callback function set when a new scan is selected on the Sigmoid docker widget.  It:

        - Sets the current scan index in the controller (:class:`~controller.Controller.set_scan_index`)
        - Switches to the new scan via the controller (:class:`~controller.Controller.switch_to_scan`)

        :param int new_scan_index: The scan index to display
        """
        self.controller.set_scan_index(new_scan_index)
        self.controller.switch_to_scan(new_scan_index)

    def update_scan_info(self):
        """
        Updates the Sigmoid Parameters widget.
        """
        # RESEARCH Find out why this method is being called twice every time a new scan is selected
        curr_scan = self.controller.scans[self.controller.curr_scan_index]
        num_scan = len(self.controller.scans)
        self.experiment_date.setText(self.controller.experiment_date)
        start_time = dt.date.strftime(curr_scan.start_time, "%H:%M:%S")
        end_time = dt.date.strftime(curr_scan.end_time, "%H:%M:%S")
        scan_time = start_time + " - " + end_time
        self.scan_time.setText(scan_time)
        self.supersaturation.setText(', '.join(map(str, np.unique(curr_scan.processed_super_sats))))
        # Update the Sigmoid Parameters section
        self.scan_selector.set_range(0, num_scan - 1)
        self.scan_selector.set_value(self.controller.curr_scan_index)
        # Update the Scan status
        if curr_scan.is_valid():
            self.scan_status.setText("VALID")
            self.scan_status.setStyleSheet("QWidget { background-color:None}")
        else:
            self.scan_status.setText("INVALID")
            self.scan_status.setStyleSheet("QWidget { color: white; background-color:red}")
        if curr_scan.sigmoid_status is None:
            self.sigmoid_status.setText("Not attempted")
            self.sigmoid_status.setStyleSheet("QWidget { background-color:None}")
        elif curr_scan.sigmoid_status:
            self.sigmoid_status.setText("VALID")
            self.sigmoid_status.setStyleSheet("QWidget { background-color:None}")
        else:
            self.sigmoid_status.setText("INVALID")
            self.sigmoid_status.setStyleSheet("QWidget { color: white; background-color:red}")
        # For all dp widgets on the screen, remove them
        for i in range(len(self.dp_widgets)):
            self.rem_params_group_box()
        # Set up for current scan's parameters
        self.num_sigmoid_lines = 0
        sigmoid_params = curr_scan.sigmoid_params
        dp50s = curr_scan.dp50
        # For each set of sigmoid parameters, create a widget and increase num_of_sigmoid_lines by one
        for i in range(len(sigmoid_params)):
            a_sigmoid_param = sigmoid_params[i]
            a_dp_param = None
            # If dp parameters already exist, set with known values
            if i < len(dp50s):
                a_dp_param = dp50s[i]
            self.add_params_group_box(a_sigmoid_param, a_dp_param)

    def update_experiment_info(self):
        """
        Updates the experiment information section of the Sigmoid Parameters widget
        """
        # Update the values
        self.experiment_date.setText(self.controller.experiment_date)

    def rem_params_group_box(self):
        """
        Reduces the number of Sigmoid Parameters by 1
        """
        # Reduce the number of sigmoid lines by one
        self.num_sigmoid_lines = max(self.num_sigmoid_lines - 1, 0)
        # Change the spinbox value
        self.sigmoid_line_spinbox.set_value(self.num_sigmoid_lines)
        # If there are still dp_widgets
        if len(self.dp_widgets) > 0:
            # RESEARCH This is too hardcoded to be flexible
            to_del = self.layout().takeAt(len(self.dp_widgets)+16)
            del self.dp_widgets[-1]
            to_del.widget().deleteLater()

    def add_params_group_box(self, sigmoid_params=None, dp50s=None):
        """
        Adds a sigmoid parameter set box which allows the user to adjust the sidmoid parameters lines and
        view the Dp50 values.

        :param list[int] sigmoid_params: A list containing the four interger values needed for the sigmoid parameters.

                                         - x_0
                                         - curve_max
                                         - k
                                         - y_0
        :param int dp50s: The DP50 value
        """
        # Set variable values
        if sigmoid_params is None:
            sigmoid_params = [0, 0, 0, 0]
        if dp50s is None:
            dp50s = 0
        else:
            dp50s = round(dp50s, 4)
        self.num_sigmoid_lines += 1
        maximum = max(self.controller.scans[self.curr_scan_index].ave_smps_diameters)  # QUESTION What should it be?
        # Update existing widgets
        self.sigmoid_line_spinbox.set_value(self.num_sigmoid_lines)
        # Create new sigmoid parameters widgets
        params_group_box = Qw.QGroupBox("Parameter Set #" + str(self.num_sigmoid_lines))
        sig_mid = c_widget.LabeledDoubleSpinbox("Sigmoid Midpoint")  # QUESTION Better echo_label wording
        sig_mid.set_maximum(maximum)
        sig_mid.set_value(np.exp(sigmoid_params[0]))
        curve_max = c_widget.LabeledDoubleSpinbox("Curve Max")  # QUESTION Better echo_label wording
        curve_max.set_maximum(maximum)
        curve_max.set_setsinglestep(0.01)
        curve_max.set_value(sigmoid_params[1])
        log_grow_rate = c_widget.LabeledDoubleSpinbox("Curve Steepness")  # QUESTION Better echo_label wording
        log_grow_rate.set_maximum(maximum)
        log_grow_rate.set_value(sigmoid_params[2])
        # Create a widget for y_0 but do not display.  Needed for "apply"  # RESEARCH
        y_0 = c_widget.LabeledDoubleSpinbox("y_0")
        y_0.set_maximum(maximum)
        y_0.set_value(sigmoid_params[3])
        v_layout = Qw.QVBoxLayout()
        v_layout.addWidget(sig_mid)
        v_layout.addWidget(curve_max)
        v_layout.addWidget(log_grow_rate)
        # -- dp50
        dp_50_label = Qw.QLabel("Dp50")
        dp_50_box = Qw.QLineEdit(str(dp50s))
        dp_50_box.setReadOnly(True)
        dp50_h_layout = Qw.QHBoxLayout()
        dp50_h_layout.addWidget(dp_50_label)
        dp50_h_layout.addWidget(dp_50_box)
        v_layout.addLayout(dp50_h_layout)
        # Add various widgets to display
        params_group_box.setLayout(v_layout)
        self.dp_widgets.append([sig_mid, curve_max, log_grow_rate, y_0])
        # RESEARCH Hard code-y values again for first parameter
        self.layout().insertRow(len(self.dp_widgets)+8, params_group_box)

    def apply_sigmoid_params(self):
        """
        Applies the sigmoid parameters and fits the new sigmoid line.
        """
        param_list = []

        for a_param_set in self.dp_widgets:
            sig_mid = np.log(a_param_set[0].content_box.value())
            curve_max = a_param_set[1].content_box.value()
            log_grow_rate = a_param_set[2].content_box.value()
            y_0 = a_param_set[3].content_box.value()
            param_list.append([sig_mid, curve_max, log_grow_rate, y_0])
        # set the sigmoid parameters and fit new sigmoid lines
        self.controller.scans[self.controller.curr_scan_index].set_sigmoid_params(param_list)
        self.controller.switch_to_scan(self.controller.curr_scan_index)


class DockerKappaWidget(Qw.QFrame):
    """
    # REVIEW Documentation

    :param controller:
    :type controller:
    :param kappa_graph:
    :type kappa_graph:
    """
    def __init__(self, controller, kappa_graph):
        # COMBAKL Kappa
        super(self.__class__, self).__init__()
        self.controller = controller
        self.kappa_graph = kappa_graph
        # set up the layout
        v_layout = Qw.QVBoxLayout()
        self.setContentsMargins(-10, -10, 0, -10)
        v_layout.setContentsMargins(30, 20, 20, 0)
        self.setAutoFillBackground(True)
        palette = Qg.QPalette()
        palette.setColor(Qg.QPalette.Background, Qc.Qt.white)
        self.setPalette(palette)
        self.setFrameShape(Qw.QFrame.StyledPanel)
        self.setFrameShadow(Qw.QFrame.Plain)
        # Layout kappa values section
        # -- groupbox to control showing k lines
        show_k_lines_groupbox = Qw.QGroupBox("Kappa lines")
        self.show_all_lines_radio_button = Qw.QRadioButton("Show all lines")
        # noinspection PyUnresolvedReferences
        self.show_all_lines_radio_button.clicked.connect(self.show_all_k_lines)  # RESEARCH connect unresolved ref
        self.show_tight_lines_radio_button = Qw.QRadioButton("Show tight lines")
        # noinspection PyUnresolvedReferences
        self.show_tight_lines_radio_button.clicked.connect(self.show_tight_k_lines)  # RESEARCH connect unresolved ref
        self.show_all_lines_radio_button.setChecked(True)
        h_layout = Qw.QHBoxLayout()
        h_layout.addWidget(self.show_all_lines_radio_button)
        h_layout.addWidget(self.show_tight_lines_radio_button)
        show_k_lines_groupbox.setLayout(h_layout)
        v_layout.addWidget(show_k_lines_groupbox)
        # -- groupbox to control showing k points
        show_k_points_groupbox = Qw.QGroupBox("Kappa values")
        self.show_all_points_radio_button = Qw.QRadioButton("Show all Ks")
        # noinspection PyUnresolvedReferences
        self.show_all_points_radio_button.clicked.connect(self.show_all_k_points)  # RESEARCH connect unresolved ref
        self.show_ave_points_radio_button = Qw.QRadioButton("Show averge Ks")
        # noinspection PyUnresolvedReferences
        self.show_ave_points_radio_button.clicked.connect(self.show_ave_k_points)  # RESEARCH connect unresolved ref
        self.show_all_points_radio_button.setChecked(True)
        h_layout = Qw.QHBoxLayout()
        h_layout.addWidget(self.show_all_points_radio_button)
        h_layout.addWidget(self.show_ave_points_radio_button)
        show_k_points_groupbox.setLayout(h_layout)
        v_layout.addWidget(show_k_points_groupbox)
        # -- Show kappa data table
        self.kappa_data_table = c_widget.KappaTableWidget(self)
        v_layout.addWidget(self.kappa_data_table)
        self.setLayout(v_layout)

    def show_all_k_lines(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_all_klines()

    def show_tight_k_lines(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_tight_klines(self.controller.alpha_pinene_dict)

    def show_all_k_points(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_all_kappa_points(self.controller.alpha_pinene_dict,
                                                 self.controller.valid_kappa_points)

    def show_ave_k_points(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        self.kappa_graph.update_average_kappa_points(self.controller.alpha_pinene_dict)

    def update_kappa_graph(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        if self.show_all_points_radio_button.isChecked():
            self.show_all_k_points()
        else:
            self.show_ave_k_points()

    def toggle_k_points(self, ss, dp, state):
        """
        # REVIEW Documentation

        :param ss:
        :type ss:
        :param dp:
        :type dp:
        :param state:
        :type state:
        """
        # COMBAKL Kappa
        ss = float(ss)
        dp = float(dp)
        self.controller.set_kappa_point_state(ss, dp, state)
        self.kappa_data_table.set_status(ss, dp, self.controller.valid_kappa_points[(dp, ss)])

    def update_kappa_values(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        for a_key in list(self.controller.kappa_calculate_dict.keys()):
            a_scan = self.controller.kappa_calculate_dict[a_key]
            for aSS in a_scan:
                ss = a_key
                scan_index = aSS[0]
                dp_50 = aSS[1]
                app_k = aSS[2]
                activation = aSS[3]
                self.kappa_data_table.add_row(scan_index, ss, dp_50, app_k,
                                              self.controller.valid_kappa_points[(scan_index, dp_50, ss, activation)])
