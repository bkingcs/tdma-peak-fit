"""
Creates small graphical objects used in other widgets and dialogs.
"""
# External Packages
import PySide2.QtCore as Qc
import PySide2.QtWidgets as Qw


###########################
# Small Graphical Widgets #
###########################

class TitleHLine(Qw.QWidget):
    """
    Creates a widget that can be used to create a title that is centered with a horizontal line on either side of it.

    :param str title: The title to appear centered between the horizontal lines
    """
    def __init__(self, title):
        super(self.__class__, self).__init__()
        h_layout = Qw.QHBoxLayout()
        h_layout.addWidget(HLineRaised())
        h_layout.addWidget(Qw.QLabel(title))
        h_layout.addWidget(HLineRaised())
        self.setLayout(h_layout)


class VLineSunk(Qw.QFrame):
    """
    Creates a vertical line QFrame.
    """
    def __init__(self):
        super(VLineSunk, self).__init__()
        self.setFrameShape(Qw.QFrame.VLine)
        self.setFrameShadow(Qw.QFrame.Sunken)


class HLineRaised(Qw.QFrame):
    """
    Creates a widget that can be used to create a horizontal line
    """
    def __init__(self):
        super(HLineRaised, self).__init__()
        self.setFrameShape(Qw.QFrame.HLine)
        self.setFrameShadow(Qw.QFrame.Raised)


############################
# Larger Graphical Widgets #
############################


class ArrowSpinBox(Qw.QWidget):
    """
    Creates a widget that can be used to click forwards and backwards in a list or select a specific index

    :param bool forward: True if clicking next should set up.  False if clicking next should step down.
    """
    def __init__(self, forward):
        super(self.__class__, self).__init__()
        h_layout = Qw.QHBoxLayout()
        self.content_box = Qw.QSpinBox()
        self.content_box.setButtonSymbols(Qw.QAbstractSpinBox.NoButtons)
        self.content_box.setMinimumWidth(100)
        self.content_box.setAlignment(Qc.Qt.AlignCenter)
        self.prev_button = Qw.QToolButton()
        self.prev_button.setArrowType(Qc.Qt.LeftArrow)
        self.next_button = Qw.QToolButton()
        self.next_button.setArrowType(Qc.Qt.RightArrow)
        if forward:
            Qc.QObject.connect(self.prev_button, Qc.SIGNAL('clicked()'), self.content_box.stepDown)
            Qc.QObject.connect(self.next_button, Qc.SIGNAL('clicked()'), self.content_box.stepUp)
        else:
            Qc.QObject.connect(self.prev_button, Qc.SIGNAL('clicked()'), self.content_box.stepUp)
            Qc.QObject.connect(self.next_button, Qc.SIGNAL('clicked()'), self.content_box.stepDown)
        h_layout.addWidget(self.prev_button)
        h_layout.addWidget(self.content_box)
        h_layout.addWidget(self.next_button)
        h_layout.setAlignment(Qc.Qt.AlignRight)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(h_layout)

    def set_callback(self, func):
        """
        Sets the function to call when a selector that uses the ArrowSpinBox is updated.

        :param instancemethod func: The function to call when the selector is updated.
        """
        # noinspection PyUnresolvedReferences
        self.content_box.valueChanged.connect(func)  # RESEARCH connect unresolved ref

    def set_value(self, value):
        """
        Sets the value in the text box of the arrow box.

        :param int value: The value to set the text box to
        """
        self.content_box.setValue(value)

    def set_range(self, min_range, max_range):
        """
        Sets the possible range of the arrow box.

        :param int min_range: The minimum value for the arrow box range
        :param int max_range: The maximum value for the arrow box range
        """
        self.content_box.setRange(min_range, max_range)


class LabeledDoubleSpinbox(Qw.QWidget):
    """
    Creates a widget that has a box for typing in a number on the left and up/down spinner buttons to the left to
    allow the user to adjust the values

    :param str title:  The title of the box which will be right aligned.
    """
    def __init__(self, title):
        super(self.__class__, self).__init__()
        self.title = title
        h_layout = Qw.QHBoxLayout()
        label = Qw.QLabel(self.title)
        self.content_box = Qw.QDoubleSpinBox()
        self.content_box.setMinimumWidth(150)
        self.content_box.setAlignment(Qc.Qt.AlignCenter)
        self.content_box.setDecimals(4)
        h_layout.addWidget(label)
        h_layout.addWidget(self.content_box)
        h_layout.setAlignment(Qc.Qt.AlignRight)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(h_layout)

    def set_setsinglestep(self, new_single_step):
        """
        Overloads the QDoubleSpinBox setSingleStep function:
        "When the user uses the arrows to change the spin box's value the value will be incremented/decremented by the
        amount of the PySide.QtGui.QDoubleSpinBox.singleStep() . The default value is 1.0. Setting a
        PySide.QtGui.QDoubleSpinBox.singleStep() value of less than 0 does nothing."

        :param float new_single_step: The maximum value allowed in the spinner box
        """
        # print("%s max_value at: %f" % (self.title, max_value))  # TODO issues/29 end_asymp_dp shows max of 99
        self.content_box.setSingleStep(new_single_step)

    def set_maximum(self, max_value):
        """
        Sets the max value allowed in the spinner.

        :param float max_value: The maximum value allowed in the spinner box
        """
        # print("%s max_value at: %f" % (self.title, max_value))  # TODO issues/29 end_asymp_dp shows max of 99
        self.content_box.setMaximum(max_value)

    def set_value(self, new_value):
        """
        Sets the new value displayed in the spinner.

        :param float new_value:  The new value to display in the spinner.
        """
        # print("%s new_value at: %f" % (self.title, new_value))  # TODO issues/29 end_asymp_dp shows max of 99
        self.content_box.setValue(new_value)


class KappaTableWidget(Qw.QTableWidget):
    """
    # REVIEW Documentation

    :param kappa_docker:
    :type kappa_docker:
    """
    def __init__(self, kappa_docker):
        # COMBAKL Kappa
        super(self.__class__, self).__init__()
        self.kappa_docker = kappa_docker
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Scan", "Status", "ss", "Dp50", "Kappa Apparent"])
        self.setSelectionBehavior(Qw.QTableWidget.SelectRows)
        # noinspection PyUnresolvedReferences
        self.itemClicked.connect(self.row_click)  # RESEARCH connect unresolved ref
        # noinspection PyUnresolvedReferences
        self.itemChanged.connect(self.toggle_row)  # RESEARCH connect unresolved ref
        # noinspection PyUnresolvedReferences
        self.itemDoubleClicked.connect(self.row_click)  # RESEARCH connect unresolved ref
        self.verticalHeader().setVisible(False)
        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 60)
        self.setColumnWidth(2, 40)
        self.setColumnWidth(3, 70)
        self.horizontalHeader().setStretchLastSection(True)

    def add_row(self, scan_index, ss, dp_50, app_k, status):
        """
        # REVIEW Documentation

        :param scan_index:
        :type scan_index:
        :param ss:
        :type ss:
        :param dp_50:
        :type dp_50:
        :param app_k:
        :type app_k:
        :param status:
        :type status:
        """
        # COMBAKL Kappa
        self.insertRow(self.rowCount())
        current_row = self.rowCount() - 1
        scan_index = Qw.QTableWidgetItem(str(int(scan_index)))
        scan_index.setFlags(Qc.Qt.ItemIsEnabled | Qc.Qt.ItemIsSelectable)
        scan_index.setTextAlignment(Qc.Qt.AlignCenter)
        status_box = Qw.QTableWidgetItem()
        if status:
            status_box.setCheckState(Qc.Qt.Checked)
            status_box.setText("Inc")
        else:
            status_box.setCheckState(Qc.Qt.Unchecked)
            status_box.setText("Exc")
        status_box.setTextAlignment(Qc.Qt.AlignCenter)
        ss = Qw.QTableWidgetItem(str(ss))
        ss.setFlags(Qc.Qt.ItemIsEnabled | Qc.Qt.ItemIsSelectable)
        ss.setTextAlignment(Qc.Qt.AlignCenter)
        dp_50 = Qw.QTableWidgetItem(str(dp_50))
        dp_50.setFlags(Qc.Qt.ItemIsEnabled | Qc.Qt.ItemIsSelectable)
        dp_50.setTextAlignment(Qc.Qt.AlignCenter)
        app_k = Qw.QTableWidgetItem(str(round(app_k, 2)))
        app_k.setFlags(Qc.Qt.ItemIsEnabled | Qc.Qt.ItemIsSelectable)
        app_k.setTextAlignment(Qc.Qt.AlignCenter)
        self.setItem(current_row, 0, scan_index)
        self.setItem(current_row, 1, status_box)
        self.setItem(current_row, 2, ss)
        self.setItem(current_row, 3, dp_50)
        self.setItem(current_row, 4, app_k)
        self.sortByColumn(2, Qc.Qt.AscendingOrder)
        self.sortByColumn(3, Qc.Qt.AscendingOrder)

    def row_click(self, item):
        """
        # REVIEW Documentation

        :param item:
        :type item:
        """
        # COMBAKL Kappa
        # if item is not the checkbox. This is because sometimes, pyqt
        # will recognize everything as checkable
        if item.column() != 0:
            return
        row = item.row()
        if self.item(row, 1) is None or self.item(row, 2) is None:
            return
        # RESEARCH Following lines of htdma_code do nothing
        # ss = self.item(row, 1).text()
        # dp = self.item(row, 2).text()

    def toggle_row(self, item):
        """
        # REVIEW Documentation

        :param item:
        :type item:
        """
        # COMBAKL Kappa
        row = item.row()
        # only check for the first column
        if item.column() != 0:
            return
        if self.item(row, 1) is None or self.item(row, 2) is None:
            return
        ss = self.item(row, 1).text()
        dp = self.item(row, 2).text()
        if item.checkState() == Qc.Qt.Unchecked:
            self.kappa_docker.toggle_k_points(ss, dp, False)
        else:
            self.kappa_docker.toggle_k_points(ss, dp, True)

    def set_status(self, ss, dp, status):
        """
        # REVIEW Documentation

        :param ss:
        :type ss:
        :param dp:
        :type dp:
        :param status:
        :type status:
        """
        # COMBAKL Kappa
        # find the right row first
        for i in range(self.rowCount()):
            if float(self.item(i, 1).text()) == ss and float(self.item(i, 2).text()) == dp:
                # this kappa point is valid
                status_box = self.item(i, 0)
                if status:
                    status_box.setCheckState(Qc.Qt.Checked)
                    status_box.setText("Included")
                else:
                    status_box.setCheckState(Qc.Qt.Unchecked)
                    status_box.setText("Excluded")
