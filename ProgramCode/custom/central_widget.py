"""
Creates the various widgets that display in the main section of the display
"""
# External Packages
import PySide2.QtCore as Qc
import PySide2.QtWidgets as Qw

# Internal Packages
import custom.widget as c_widget


class CentralWidgetScans(Qw.QWidget):
    """
    Creates the central widget that displays the four graphs.

    :param MainView parent: The main view that is creating the central scan widget in order to access the graphs.
    """
    def __init__(self, parent):
        super(self.__class__, self).__init__()
        # Create the widgets
        self.main_view = parent
        self.raw_conc_time_graph = self.main_view.raw_conc_time_graph
        self.smoothed_conc_time_graph = self.main_view.smoothed_conc_time_graph
        self.ratio_dp_graph = self.main_view.ratio_dp_graph
        self.temp_graph = self.main_view.temp_graph
        # Split the screen and add the widgets to the section
        self.h_splitter_1 = Qw.QSplitter(Qc.Qt.Horizontal)
        self.h_splitter_1.addWidget(self.raw_conc_time_graph)
        self.h_splitter_1.addWidget(self.smoothed_conc_time_graph)
        self.h_splitter_2 = Qw.QSplitter(Qc.Qt.Horizontal)
        self.h_splitter_2.addWidget(self.ratio_dp_graph)
        self.h_splitter_2.addWidget(self.temp_graph)
        self.v_splitter = Qw.QSplitter(Qc.Qt.Vertical)
        self.v_splitter.addWidget(self.h_splitter_1)
        self.v_splitter.addWidget(self.h_splitter_2)
        hbox = Qw.QHBoxLayout(self)
        hbox.addWidget(self.v_splitter)
        # Create the divider lines and add the widgetst to the display
        handle = self.h_splitter_1.handle(1)
        a_layout = Qw.QVBoxLayout()
        a_layout.setSpacing(0)
        a_layout.setContentsMargins(0, 0, 0, 0)
        a_layout.addWidget(c_widget.VLineSunk())
        handle.setLayout(a_layout)
        handle = self.h_splitter_2.handle(1)
        a_layout = Qw.QVBoxLayout()
        a_layout.setSpacing(0)
        a_layout.setContentsMargins(0, 0, 0, 0)
        a_layout.addWidget(c_widget.VLineSunk())
        handle.setLayout(a_layout)
        handle = self.v_splitter.handle(1)
        a_layout = Qw.QHBoxLayout()
        a_layout.setSpacing(0)
        a_layout.setContentsMargins(0, 0, 0, 0)
        a_layout.addWidget(c_widget.HLineRaised())
        handle.setLayout(a_layout)
        self.setLayout(hbox)


class CentralWidgetKappa(Qw.QWidget):
    """
    Creates the central widget that displays the kappa graph.

    :param MainView parent: The main view that is creating the central kappa widget in order to access the graphs.
    """
    def __init__(self, parent):
        # COMBAKL Kappa
        super(self.__class__, self).__init__()
        # Add widgets
        self.main_view = parent
        self.kappa_graph = self.main_view.kappa_graph
        v_layout = Qw.QVBoxLayout(self)
        v_layout.addWidget(self.kappa_graph)
        self.setLayout(v_layout)
