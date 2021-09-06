

import sys

import matplotlib as mpl
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from code.model.model import Model

mpl.use('Qt5Agg')

class DMA_1_Graph_Widget(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(DMA_1_Graph_Widget, self).__init__(self.fig)

        self.model = None

    def set_model(self, model: Model):
        self.model = model
        self.update_plot()

    def update_plot(self):
        # Remove the previous axes
        self.fig.delaxes(self.axes)

        # Create a new axes
        self.axes = self.fig.add_subplot(111)

        # Update it from the model
        self.model.dma1.plot(self.axes)

        # TODO - Not sure which if any of these draw methods are needed
        # self.draw_idle()
        self.fig.canvas.draw_idle()

