"""
Creates the various widgets that display in the main section of the display
"""
# External Packages
import PySide2.QtCore as Qc
import PySide2.QtWidgets as Qw

# Internal Packages


class CentralWidgetScans(Qw.QWidget):
    """
    Creates the central widget that displays the four graphs.

    :param MainView parent: The main view that is creating the central scan widget in order to access the graphs.
    """
    def __init__(self, parent):
        super(self.__class__, self).__init__()
        # Create the widgets
        self.main_view = parent

        # Let's grab the graph objects from the main view class
        self.dma1_graph = self.main_view.dma1_graph
        self.second_graph = self.main_view.second_graph
        self.third_graph = self.main_view.third_graph
        self.fourth_graph = self.main_view.fourth_graph

        # Split the screen and add the widgets to the section
        self.h_splitter_1 = Qw.QSplitter(Qc.Qt.Horizontal)
        self.h_splitter_1.addWidget(self.dma1_graph)
        self.h_splitter_1.addWidget(self.second_graph)
        self.h_splitter_2 = Qw.QSplitter(Qc.Qt.Horizontal)
        self.h_splitter_2.addWidget(self.third_graph)
        self.h_splitter_2.addWidget(self.fourth_graph)
        self.v_splitter = Qw.QSplitter(Qc.Qt.Vertical)
        self.v_splitter.addWidget(self.h_splitter_1)
        self.v_splitter.addWidget(self.h_splitter_2)
        hbox = Qw.QHBoxLayout(self)
        hbox.addWidget(self.v_splitter)
        # Create the divider lines and add the widgets to the display
        # handle = self.h_splitter_1.handle(1)
        # a_layout = Qw.QVBoxLayout()
        # a_layout.setSpacing(0)
        # a_layout.setContentsMargins(0, 0, 0, 0)
        # a_layout.addWidget(c_widget.VLineSunk())
        # handle.setLayout(a_layout)
        # handle = self.v_splitter.handle(1)
        # a_layout = Qw.QHBoxLayout()
        # a_layout.setSpacing(0)
        # a_layout.setContentsMargins(0, 0, 0, 0)
        # a_layout.addWidget(c_widget.HLineRaised())
        # handle.setLayout(a_layout)
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
