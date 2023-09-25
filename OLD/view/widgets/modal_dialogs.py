"""
Creates the various dialog boxes.
"""
# External Packages
import datetime as dt
import PySide2.QtGui as Qg
import PySide2.QtWidgets as Qw


class ScanDataDialog(Qw.QDialog):
    """
    Shows the scan's detailed data to the user

    :param Scan scan: The scan to show the data for.
    """
    # TODO issues/35
    def __init__(self, scan):
        super(self.__class__, self).__init__()
        # initiate the layout
        form_layout = Qw.QFormLayout()
        # scan status
        self.additional_information = Qw.QTextEdit("-")
        self.additional_information.setReadOnly(True)
        self.additional_information.setMaximumHeight(100)
        if scan.is_valid():
            self.scan_status = Qw.QLabel("VALID")
            self.scan_status.setStyleSheet("QWidget { background-color:None}")
            self.additional_information.setText("The scan shows no problem.")
        else:
            self.scan_status = Qw.QLabel("INVALID")
            self.scan_status.setStyleSheet("QWidget { color: white; background-color:red}")
            self.additional_information.setText(scan.get_status_code_descript())
        form_layout.addRow("Scan status", self.scan_status)
        form_layout.addRow("Status Info", self.additional_information)
        # Scan times and Duration
        h_layout = Qw.QHBoxLayout()
        time_group_box = Qw.QGroupBox()
        # -- Start time
        h_layout.addWidget(Qw.QLabel("Start time"))
        start_time = dt.datetime.strftime(scan.start_time, "%H:%M:%S")
        start_time_box = Qw.QLineEdit(start_time)
        start_time_box.setReadOnly(True)
        h_layout.addWidget(start_time_box)
        # -- End time
        h_layout.addWidget(Qw.QLabel("End Time"))
        end_time = dt.date.strftime(scan.end_time, "%H:%M:%S")
        end_time_box = Qw.QLineEdit(end_time)
        end_time_box.setReadOnly(True)
        h_layout.addWidget(end_time_box)
        # -- Duration
        h_layout.addWidget(Qw.QLabel("Duration"))
        duration = str(scan.duration)
        duration_box = Qw.QLineEdit(duration)
        duration_box.setReadOnly(True)
        h_layout.addWidget(duration_box)
        # Add widgets
        time_group_box.setLayout(h_layout)
        form_layout.addRow("Times and duration", time_group_box)
        self.setLayout(form_layout)


class SettingDialog(Qw.QDialog):
    """
    Allows the user to change the program's seetings.

    :param MainView main_view: The main view of the program.
    """
    # TODO issues/46
    def __init__(self, main_view):
        super(self.__class__, self).__init__()
        self.main_view = main_view
        form_layout = Qw.QFormLayout()
        ######################
        # Fonts
        h_layout = Qw.QHBoxLayout()
        self.font_selector = Qw.QFontComboBox()
        self.font_selector.setCurrentFont(Qg.QFont("Calibri"))
        # noinspection PyUnresolvedReferences
        self.font_selector.currentFontChanged.connect(self.font_changed)   # RESEARCH connect unresolved ref
        h_layout.addWidget(self.font_selector)
        self.size_selector = Qw.QSpinBox()
        self.size_selector.setValue(12)
        # noinspection PyUnresolvedReferences
        self.size_selector.valueChanged.connect(self.font_size_changed)  # RESEARCH connect unresolved ref
        h_layout.addWidget(self.size_selector)
        form_layout.addRow("Fonts", h_layout)
        ######################
        button_boxes = Qw.QDialogButtonBox()
        apply_button = button_boxes.addButton("Ok", Qw.QDialogButtonBox.AcceptRole)
        apply_button.clicked.connect(self.accept)
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    def font_changed(self, font):
        """
        Updates the font style used throughout the program.  Does not include font used on charts.

        :param PySide.QtGui.QFont font: The new font style.
        """
        # RESEARCH Can it include the charts?
        self.main_view.set_font(font, self.size_selector.value())

    def font_size_changed(self, size):
        """
        Updates the font size used throughout the program.  Does not include font size used on charts.

        :param int size: The new font size
        """
        # RESEARCH Can it include the charts?
        self.main_view.set_font(self.font_selector.currentFont(), size)


class SelectParamsKappaDialog(Qw.QDialog):
    """
    # REVIEW Documentation

    :param controller:
    :type controller:
    """
    def __init__(self, controller):
        # COMBAKL Kappa
        super(self.__class__, self).__init__()
        self.controller = controller
        self.setWindowTitle("Select parameters for kappa calculation!")
        # QUESTION - Decimal Places
        # QUESTION - Max Values
        # --- Sigma
        self.sigma_spinbox = Qw.QDoubleSpinBox()
        self.sigma_spinbox.setDecimals(3)
        self.sigma_spinbox.setMaximum(1)
        self.sigma_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        self.sigma_spinbox.setValue(self.controller.sigma)
        # --- Temp
        self.temp_spinbox = Qw.QDoubleSpinBox()
        self.temp_spinbox.setDecimals(2)
        self.temp_spinbox.setMaximum(self.controller.temp * 2)
        self.temp_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        self.temp_spinbox.setValue(self.controller.temp)
        # --- Dry Diameter 1
        self.dd_1_spinbox = Qw.QDoubleSpinBox()
        self.dd_1_spinbox.setDecimals(2)
        self.dd_1_spinbox.setMaximum(self.controller.dd_1 * 2)
        self.dd_1_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        self.dd_1_spinbox.setValue(self.controller.dd_1)
        # --- Dry Diameter 2
        self.dd_2_spinbox = Qw.QDoubleSpinBox()
        self.dd_2_spinbox.setDecimals(2)
        self.dd_2_spinbox.setMaximum(self.controller.dd_1 * 2)
        self.dd_2_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        self.dd_2_spinbox.setValue(self.controller.dd_2)
        # --- iKappa1
        self.i_kappa_1_spinbox = Qw.QDoubleSpinBox()
        self.i_kappa_1_spinbox.setDecimals(5)
        self.i_kappa_1_spinbox.setMaximum(1)
        self.i_kappa_1_spinbox.setValue(self.controller.i_kappa_1)
        self.i_kappa_1_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        # --- iKappa2
        self.i_kappa_2_spinbox = Qw.QDoubleSpinBox()
        self.i_kappa_2_spinbox.setDecimals(5)
        self.i_kappa_2_spinbox.setMaximum(self.controller.i_kappa_2 * 2)
        self.i_kappa_2_spinbox.setValue(self.controller.i_kappa_2)
        self.i_kappa_2_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        # --- solubility
        self.solubility_spinbox = Qw.QDoubleSpinBox()
        self.solubility_spinbox.setDecimals(5)
        self.solubility_spinbox.setMaximum(1)
        self.solubility_spinbox.setValue(self.controller.solubility)
        self.solubility_spinbox.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        # -- Layout
        form_layout = Qw.QFormLayout()
        form_layout.addRow(self.tr("&Sigma"), self.sigma_spinbox)
        form_layout.addRow(self.tr("&Temperature"), self.temp_spinbox)
        form_layout.addRow(self.tr("&dry diameter(1)"), self.dd_1_spinbox)
        form_layout.addRow(self.tr("&iKappa(1)"), self.i_kappa_1_spinbox)
        form_layout.addRow(self.tr("&dry diameter(2)"), self.dd_2_spinbox)
        form_layout.addRow(self.tr("&iKappa(2)"), self.i_kappa_2_spinbox)
        form_layout.addRow(self.tr("&solubility"), self.solubility_spinbox)
        button_boxes = Qw.QDialogButtonBox()
        apply_button = button_boxes.addButton("Apply", Qw.QDialogButtonBox.ApplyRole)
        apply_button.clicked.connect(self.apply)
        form_layout.addWidget(button_boxes)
        self.setLayout(form_layout)

    def apply(self):
        """
        # REVIEW Documentation
        """
        # COMBAKL Kappa
        # transfer all of the values to the controller
        self.controller.set_sigma(self.sigma_spinbox.value())
        self.controller.set_temp(self.temp_spinbox.value())
        self.controller.set_dd_1(self.dd_1_spinbox.value())
        self.controller.set_dd_2(self.dd_2_spinbox.value())
        self.controller.set_i_kappa_1(self.i_kappa_1_spinbox.value())
        self.controller.set_i_kappa_2(self.i_kappa_2_spinbox.value())
        self.controller.set_solubility(self.solubility_spinbox.value())
        self.accept()
        self.controller.cal_kappa()
