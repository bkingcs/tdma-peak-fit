"""
This represents the widget that will encapsulate the actual scan data and
associated plot
"""

import sys

import matplotlib as mpl
import matplotlib.pyplot as plt


mpl.use('Qt5Agg')
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from htdma_code.model.model import Model
from htdma_code.view.plot_utils import plot_scan_and_residuals

class Scan_Data_Graph_Widget(FigureCanvasQTAgg):

    def __init__(self, model: Model, parent=None, width=5, height=4, dpi=100):

        self.fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.gridspec = self.fig.add_gridspec(4,1)
        super(Scan_Data_Graph_Widget, self).__init__(self.fig)

        # The primary model that is being visualized in the graph
        self.model = model

        # The data plot
        self.ax_data = None

        # The residuals plot
        self.ax_residuals = None

        self.update_plot()

    def update_plot(self):
        # Remove the previous axes
        if self.ax_data:
            self.fig.delaxes(self.ax_data)
            self.ax_data = None
        if self.ax_residuals:
            self.fig.delaxes(self.ax_residuals)
            self.ax_residuals = None

        # Create a new axes by dividing up the region into 4 parts, 3 will be
        # dedicated to the data, and 1 to the residuals
        self.ax_data = self.fig.add_subplot(self.gridspec[0:3,0])
        self.ax_residuals = self.fig.add_subplot(self.gridspec[3,0],
                                                 sharex=self.ax_data)

        # Turn off the axis labels on the top
        plt.setp(self.ax_data.get_xticklabels(), visible=False)

        # Update it from the model
        if self.model.current_scan:
            plot_scan_and_residuals(self.model.current_scan,
                                    self.ax_data,self.ax_residuals)
            self.gridspec.tight_layout(self.fig)

        # Set the y limits to the max_y if it is provided
        if not self.model.scan_graph_auto_scale_y:
            self.ax_data.set_ylim(0, self.model.scan_graph_max_y)

        # TODO - Not sure which if any of these draw methods are needed
        # self.draw_idle()
        self.fig.canvas.draw_idle()
