"""
Initalizes and updates the graphs
"""
# External Packages
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

# Internal Packages
# import data.klines
# import helper_functions as hf
from htdma_code.model import DMA_1

class FirstDMA(FigureCanvas):
    """
    Plot the graph that represents the first DMA theoretical distribution
    """
    def __init__(self, dma1: DMA_1 = None):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)

        plt.style.use('seaborn-whitegrid')

        if dma1:
            dma1.plot(self.fig, self.ax)

    def update(self,dma1: DMA_1):
        if dma1:
            dma1.plot(self.fig, self.ax)

class SecondGraph(FigureCanvas):
    """
    Plotting a graph to start creating plain graphs for when
    the htdma_code comes in
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots(2)
        super(self.__class__, self).__init__(self.fig)

        # setting up points for the graph
        x = np.linspace(0, 2 * np.pi, 400)
        y = np.sin(x ** 2)

        # plotting the graph
        self.ax[0].plot(x, y)
        self.ax[1].plot(x, -y)

        # set up the figure and the axes
        self.fig.suptitle("Practice Plot Graph")


class ThirdGraph(FigureCanvas):
    """
    Plotting a graph to start creating plain graphs for when
    the htdma_code comes in
    """
    def __init__(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2)
        super(self.__class__, self).__init__(self.fig)

        # setting up points for the graph
        x = np.linspace(0, 2 * np.pi, 400)
        y = np.sin(x ** 2)

        # plotting the graph
        self.ax1.plot(x, y)
        self.ax2.plot(x, -y)

        # set up the figure and the axes
        self.fig.suptitle("Practice Plot Graph")

        # set up the figure and the axes
        # self.ax.set_title("Practice Plot Graph")
        # self.ax.set_xlabel("Numbers")
        # self.ax.set_ylabel("More Numbers")

class FourthGraph(FigureCanvas):
    """
    Plotting a graph to start creating plain graphs for when
    the htdma_code comes in
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super(self.__class__, self).__init__(self.fig)

        # set up the figure and the axes
        # self.ax.set_title("Practice Plot Graph")
        # self.ax.set_xlabel("Numbers")
        # self.ax.set_ylabel("More Numbers")

        # get the data calculated for the normal distribution
        data = self.normal_distribution()

        # create histogram
        n, bins, patches = self.ax.hist(data, bins='auto', rwidth=0.85, alpha=0.75)

        # set up the figure and the axes
        self.fig.suptitle("Normal Distribution")

        # plot graph
        plt.tight_layout()


    def normal_distribution(self):
        num_points = 50
        mean = 60
        standard_deviation = 15
        np.random.seed(42)
        data = np.random.normal(mean, standard_deviation, num_points)
        return data

    def plot_graph(self):
        data = self.normal_distribution()

        num_points, bins, patches = plt.hist(data, bins='auto', rwidth=0.85, alpha=0.75)

        plt.show()

# class KappaGraph(FigureCanvas):
#     """
#     # REVIEW Documentation
#     """
#     def __init__(self):
#         self.fig, self.ax = plt.subplots()
#         super(self.__class__, self).__init__(self.fig)
#         # set up the figure and axes
#         # self.ax.set_title("")  # TODO
#         self.ax.set_xlabel("Dry diameter(nm)")
#         self.ax.set_ylabel("Supersaturation(%)")
#         # set up klines  # TODO See if csv file is an issue for standalone exe
#         self.klines_data = pd.read_csv(StringIO(data.klines.csv_codes), header=1)
#         self.header = self.klines_data.columns
#         self.klines_diameters = self.klines_data[self.header[1]]
#         # set up empty data lines
#         self.valid_kappa_points, = self.ax.plot([], [], "o", echo_label="Valid K-points")
#         self.invalid_kappa_points, = self.ax.plot([], [], "x", echo_label="Invalid K-points")
#         self.average_kappa_points, = self.ax.plot([], [], "o", echo_label="Average K-points")
#         self.klines = []
#
#         annotation = self.ax.annotate("", xy=(0, 0), xytext=(20, 20), textcoords="offset points",
#                                       bbox=dict(boxstyle="round", fc="0.8"),
#                                       arrowprops=dict(arrowstyle="fancy", connectionstyle="angle3,angleA=0,angleB=-90"))
#         annotation.set_visible(False)
#
#         def update_annotation(details, a_line):
#             """
#             # REVIEW Documentation
#
#             :param details:
#             :type details:
#             :param a_line:
#             :type a_line:
#             :return:
#             :rtype:
#             """
#             x_line, y_line = a_line.get_data()
#             annotation.xy = (x_line[details["ind"][0]], y_line[details["ind"][0]])
#             if a_line.get_gid() is not None:
#                 annotation.set_text(a_line.get_gid())
#             else:
#                 text = format("DP50: %.1f  SS:%.1f" % (x_line[details["ind"][0]], y_line[details["ind"][0]]))
#                 annotation.set_text(text)
#
#         def on_plot_hover(event):
#             """
#             # REVIEW Documentation
#
#             :param event:
#             :type event:
#             :return:
#             :rtype:
#             """
#             if event.inaxes == self.ax:
#                 is_annotation_visable = annotation.get_visible()
#                 for a_line in self.ax.get_lines():
#                     contains, details = a_line.contains(event)
#                     if contains:
#                         update_annotation(details, a_line)
#                         annotation.set_visible(True)
#                         self.fig.canvas.draw_idle()
#                     else:
#                         if is_annotation_visable:
#                             annotation.set_visible(False)
#                             self.fig.canvas.draw_idle()
#
#         self.fig.canvas.mpl_connect('motion_notify_event', on_plot_hover)
#
#         # COMBAKL Kappa
#         self.update_all_klines()
#         plt.subplots_adjust(right=0.8)
#         plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
#         # plot graph
#         # plt.tight_layout()
#
#     def update_tight_klines(self, alpha_pinene_dict):
#         """
#         # REVIEW Documentation
#
#         :param alpha_pinene_dict:
#         :type alpha_pinene_dict:
#         """
#         # COMBAKL Kappa
#         kappa_list = []
#         std_kappa_list = []
#         # get a list of kappa values and std
#         for a_key in alpha_pinene_dict:
#             kappa_list.append(alpha_pinene_dict[a_key][2])
#             std_kappa_list.append(alpha_pinene_dict[a_key][3])
#         max_kappa = max(kappa_list) + max(std_kappa_list)
#         min_kappa = min(kappa_list) - max(std_kappa_list)
#         # now, find the position of the start column and end column that correspond to the max and
#         # min kappa
#         i = 2
#         kappa = 1
#         step = 0.1
#         while True:
#             if max_kappa > kappa:
#                 kline_start_column = max(2, i - 3)
#                 break
#             i += 1
#             kappa -= step
#             if kappa == step:
#                 step /= 10
#             if i >= len(self.header):
#                 kline_start_column = len(self.header)
#                 break
#         i = 2
#         kappa = 1
#         step = 0.1
#         while True:
#             if min_kappa > kappa:
#                 kline_end_column = min(i + 3, len(self.header))
#                 break
#             i += 1
#             kappa -= step
#             if kappa == step:
#                 step /= 10
#             if i >= len(self.header):
#                 kline_end_column = len(self.header)
#                 break
#         self.graph_klines(kline_start_column, kline_end_column)
#
#     def update_all_klines(self):
#         """
#         # REVIEW Documentation
#         """
#         # COMBAKL Kappa
#         kline_start_column = 2
#         kline_end_column = len(self.header)
#         self.graph_klines(kline_start_column, kline_end_column)
#
#     def graph_klines(self, kline_start_column, kline_end_column):
#         """
#         # REVIEW Documentation
#
#         :param kline_start_column:
#         :type kline_start_column:
#         :param kline_end_column:
#         :type kline_end_column:
#         """
#         # COMBAKL Kappa
#         # clean up previous lines
#         for i in range(len(self.klines)):
#             self.ax.lines.remove(self.klines[i])
#         self.klines = []
#         for i in range(kline_start_column, kline_end_column):
#             y = self.klines_data[self.header[i]]
#             self.klines.append(self.ax.loglog(self.klines_diameters, y,
#                                               gid=str(self.header[i]), echo_label=str(self.header[i]), linewidth=1)[0])
#
#         plt.subplots_adjust(right=0.8)
#         plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
#         self.draw_idle()
#         self.flush_events()
#
#     def update_all_kappa_points(self, alpha_pinene_dict, valid_kappa_points):
#         """
#         # REVIEW Documentation
#
#         :param alpha_pinene_dict:
#         :type alpha_pinene_dict:
#         :param valid_kappa_points:
#         :type valid_kappa_points:
#         """
#         # COMBAKL Kappa
#         x_valid_ks = []
#         y_valid_ks = []
#         x_invalid_ks = []
#         y_invalid_ks = []
#         # print valid_kappa_points
#         # REVIEW kset use alpha pinene
#         for a_key in list(alpha_pinene_dict.keys()):
#             for v in alpha_pinene_dict[a_key][-1]:
#                 scan_index = v[0]
#                 dp50 = v[1]
#                 activation = v[2]
#                 # REVIEW kset use valid kappa points
#                 if valid_kappa_points[scan_index, dp50, a_key, activation]:
#                     x_valid_ks.append(dp50)
#                     y_valid_ks.append(a_key)
#                 else:
#                     x_invalid_ks.append(dp50)
#                     y_invalid_ks.append(a_key)
#         # update the valid points
#         self.valid_kappa_points.set_xdata(x_valid_ks)
#         self.valid_kappa_points.set_ydata(y_valid_ks)
#         # update the invalid points
#         self.invalid_kappa_points.set_xdata(x_invalid_ks)
#         self.invalid_kappa_points.set_ydata(y_invalid_ks)
#         # remove the average lines
#         self.average_kappa_points.set_xdata([])
#         self.average_kappa_points.set_ydata([])
#         self.ax.set_title("Activation Diameter for all Kappa points and Lines of Constant Kappa (K)")
#         plt.subplots_adjust(right=0.8)
#         plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
#         self.draw()
#         self.flush_events()
#
#     def update_average_kappa_points(self, alpha_pinene_dict):
#         """
#         # REVIEW Documentation
#
#         :param alpha_pinene_dict:
#         :type alpha_pinene_dict:
#         """
#         # COMBAKL Kappa
#         x_valid_ks = []
#         y_valid_ks = []
#         for a_key in list(alpha_pinene_dict.keys()):
#             if not math.isnan(alpha_pinene_dict[a_key][0]):
#                 x_valid_ks.append(alpha_pinene_dict[a_key][0])
#                 y_valid_ks.append(a_key)
#         # update the average lines
#         self.average_kappa_points.set_xdata(x_valid_ks)
#         self.average_kappa_points.set_ydata(y_valid_ks)
#         # remove other lines
#         self.valid_kappa_points.set_xdata([])
#         self.valid_kappa_points.set_ydata([])
#         self.invalid_kappa_points.set_xdata([])
#         self.invalid_kappa_points.set_ydata([])
#         self.ax.set_title("Activation Diameter for average Kappa points and Lines of Constant Kappa (K)")
#         plt.subplots_adjust(right=0.8)
#         plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
#         self.draw()
#         self.flush_events()
