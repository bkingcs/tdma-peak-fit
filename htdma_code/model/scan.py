"""
This class represents a single Scan from a run. This code will handle
everything related to one scan, including curve fitting.



Let's recall the standard normal distribution as defined by the quintessential probability density function:
- https://en.wikipedia.org/wiki/Normal_distribution

- $f(x) = \frac{1}{\sigma \sqrt{2 \pi}}e^{-\frac{1}{2}(\frac{x - \mu}{\sigma})^2}$

I'm following lots of ideas online of basic gaussian curve fits

- http://www.emilygraceripka.com/blog/16

"""
from typing import List

import numpy as np
import pandas as pd
from scipy.signal import peak_widths
from statsmodels.stats.stattools import durbin_watson
import scipy
import scipy.signal
import scipy.optimize

from PySide2.QtGui import QStandardItemModel, QStandardItem

import matplotlib as mpl
import matplotlib.pyplot as plt

##### Our fit functions

def _1gaussian(x, amp1,mu1,sigma1):
    return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-mu1)/sigma1)**2)))

def _2gaussian(x, amp1, mu1, sigma1, amp2, mu2, sigma2):
    return _1gaussian(x,amp1,mu1,sigma1) + _1gaussian(x,amp2,mu2,sigma2)
        # return amp1*(1/(sigma1*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-mu1)/sigma1)**2))) +  \
        #        amp2*(1/(sigma2*(np.sqrt(2*np.pi))))*(np.exp((-1.0/2.0)*(((x-mu2)/sigma2)**2)))

def _3gaussian(x, amp1, mu1, sigma1, amp2, mu2, sigma2, amp3, mu3, sigma3):
    return _1gaussian(x,amp1,mu1,sigma1) + \
           _1gaussian(x,amp2,mu2,sigma2) + \
           _1gaussian(x,amp3,mu3,sigma3)

def _4gaussian(x, amp1, mu1, sigma1, amp2, mu2, sigma2, amp3, mu3, sigma3, amp4, mu4, sigma4):
    return _1gaussian(x,amp1,mu1,sigma1) + \
           _1gaussian(x,amp2,mu2,sigma2) + \
           _1gaussian(x,amp3,mu3,sigma3) + \
           _1gaussian(x,amp4,mu4,sigma4)

def _5gaussian(x, amp1, mu1, sigma1, amp2, mu2, sigma2, amp3, mu3, sigma3, amp4, mu4, sigma4, amp5, mu5, sigma5):
    return _1gaussian(x,amp1,mu1,sigma1) + \
           _1gaussian(x,amp2,mu2,sigma2) + \
           _1gaussian(x,amp3,mu3,sigma3) + \
           _1gaussian(x,amp4,mu4,sigma4) + \
           _1gaussian(x,amp5,mu5,sigma5)

# fit_functions - this is the array of possible functions to fit the data to, depending on the
# number of peaks specified in the data
fit_functions = [_1gaussian,
                 _2gaussian,
                 _3gaussian,
                 _4gaussian,
                 _5gaussian]

# Constants
MAX_PEAKS_TO_FIT = 5
MIN_GOOD_WINDOW_SIZE = 5
NUM_FIT_PASSES = 1

# How close to the edges of the signal do we allow peaks?
INDEX_OF_PEAK_BOUNDS = 3

class PeakFitResult:
    """
    Encapsulate results from each peak identified in the scan

        index = the index of the peak
        dp = center of gaussian (diameter)
        sd = standard deviation of gaussian
        height = amplitude of gaussian
        fwhh = full width half height of gaussian
        growth_factor = growth factor from dp of dma 1
        kappa = computed from growth factor
        fit_params = parameters identified for best fit for this single Gaussian
    """
    def __init__(self):
        self.index = None
        self.dp = None
        self.sd = None
        self.height = None
        self.fwhh = None    # 2.3548 * sigma
        self.growth_factor = None
        self.kappa = None
        self.fit_params = None

    def __repr__(self):
        s = str(self.index) + ":\n"
        s = s + "  dp:     {:.3f}\n".format(self.dp)
        s = s + "  sd:     {:.3f}\n".format(self.sd)
        s = s + "  height: {:.3f}\n".format(self.height)
        s = s + "  fwhh:   {:.3f}\n".format(self.fwhh)
        s = s + "  gf:     {:.3f}\n".format(self.growth_factor)
        s = s + "  kappa:  {:.3f}\n".format(self.kappa)
        return s

class TotalFitResult:
    """
    Encapsulate all results for the total fit of the scan

        predicted_peak_indices = list of initial peak indicies
        num_peaks = number of peaks fitted
        fit_params = actual list of all of the parameters optimized for the fit
        fit_values = the actual fitted values
        residuals = the residuals (raw - fit)
        residuals_smoothed = residuals with moving average (for peak finding)
        residual_peak_indices = the indices of the peaks identified in the residual curve
        residuals_mean = the mean of the residuals (should be ~0)
        rmse = the root mean square error of the fit
        durbin_watson = statistic to assess independence of residual values [0-4, 2 is best]
    """
    def __init__(self):
        self.predicted_peak_indices = None
        self.num_peaks = None
        self.fit_params = None
        self.fit_values = None
        self.residuals = None
        self.residuals_smoothed = None
        self.residuals_mean = None
        self.rmse = None
        self.durbin_watson = None


    def __repr__(self):
        s = "rmse: {:.3f}\n".format(self.rmse)
        s = s + "Durbin-Watson: {:.3f}".format(self.durbin_watson)
        return s

class Scan:
    """
    Scan encapsulates a single scan of data

    Attributes:
        -
    """
    def __init__(self, scan_index: int, df: pd.DataFrame, num_dp_values: int):
        """
        This function is passed a single scan column from the time
        stamp right through the end of the column

        :param scan_index: Index of this scan in the run
        :param df: A data frame representing all row data for this scan
        :param num_dp_values: number of dp values in the scan
        """

        self.num_scan_rows = num_dp_values
        self.scan_index = scan_index

        # Let's keep an internal dataframe of the data, for now...
        self._df_data = df.iloc[1:1+self.num_scan_rows, [0]].copy()
        self._df_data.index = self._df_data.index.astype(float)
        self._df_data = self._df_data.astype(float)

        # Extract out numpy arrays of the data for speed
        self.dp_range = self._df_data.index.to_numpy()
        self.log_dp_range = np.log(self.dp_range)
        self.raw_values = self._df_data.iloc[:,0].to_numpy()

        # Preprocess / clean data to prepare for curve fit
        self._y_filtered, self._y_sel_good = self._filter_bad_values()
        self._yfit = None
        self._y_weights = None

        # Parameters that are set by the fit function
        self.num_peaks_predicted = None # Number of peaks found by find_peaks

        self.total_fit_result: TotalFitResult = None
        self.peak_fit_results: List[PeakFitResult] = None

        # self.peaks_item_model = QStandardItemModel()
        # x = self.peaks_item_model.item(2,3)

    def _filter_bad_values(self):
        """
        Internal helper function to identify points that should NOT be used in the
        curve fit

        #1) If < MIN_GOOD_WINDOW_SIZE sequential points are surrounded by 0 values, flatten them
        #2) Ignore the first and last channel values

        :return: The filtered values, and the boolean selection array indicating
        where the values are good
        """

        # Start with selecting all data
        y_sel_good = np.array([True for i in range(self.raw_values.shape[0])])

        # We know off the bat that we can eliminate the first and last channel values
        y_sel_good[0] = False
        y_sel_good[-1] = False

        # Now, carefully iterate through the ordered data. Look for small windows surrounded by zero values.
        # These should be eliminated
        is_in_good_window = False
        count_good_channels = 0
        i_good_channel_start = None
        for i in range(1,self.raw_values.shape[0]-1):
            # Is this a good channel?
            if self.raw_values[i] > 0:
                # Were we in a good window? Then keep counting it..
                if is_in_good_window:
                    count_good_channels += 1

                # We were NOT in a good window, so start one!
                else:
                    is_in_good_window = True
                    i_good_channel_start = i
                    count_good_channels = 1

            # DOH! This is a shit channel. If we had a small window, flatten the data
            else:
                # Did we have a streak of good channels?
                if is_in_good_window:
                    # Was our window of good channels too small to count it?
                    if count_good_channels < MIN_GOOD_WINDOW_SIZE:
                        # Yes? Then eliminate these points
                        for j in range(i_good_channel_start,i):
                            y_sel_good[j] = False
                    count_good_channels = 0
                    is_in_good_window = False
                y_sel_good[i] = False

        # We're done! Flatten the bad channels
        y_filtered = np.copy(self.raw_values)
        y_filtered[np.logical_not(y_sel_good)] = 0.0

        # Return the filtered data, and the selection array indicating where the good values are
        return y_filtered, y_sel_good

    def __repr__(self):
        s = "dp range: {}\n".format(repr(self.dp_range))
        s += "values: {}\n".format(repr(self.raw_values))

        return s

    def get_dp_range(self):
        """
        Get the array of dp values that were read in from the data file

        :return: A numpy array of dp values
        """
        return self.dp_range

    def get_log_dp_range(self):
        """
        Get the array of log dp values (which is nothing more than np.log on the
        actual dp values. These are needed for the curve fit

        :return: An numpy array of log dp values
        """
        return self.log_dp_range

    def get_values(self):
        """
        :return: the *unfiltered* raw concentraction values read in for this run
        """
        return self.raw_values

    def get_max_value(self):
        """
        :return: the maximum value in the raw concentration values
        """
        return self.raw_values.max()

    def fit(self, num_peaks_desired, verbose = False, plot_steps = False, plot_func = None):
        """
        This is the mother function that performs the curve fit. The results of the fit
        are stored in two separate classes:

        self.peak_fit_results --> list of PeakFitResult objects
        self.total_fit_result --> TotalFitResult
        self.num_peaks_predicted --> number of peaks predicted by peak finding scipy method

        TODO - Improve the fitting to use weights

        :param num_peaks_desired: For the time, the user must specify the number of peaks
        expected in the data.
        :param verbose: print out info while doing the fit?
        :param plot_steps: plot the fit after each step?
        :param plot_func: Sadly necessary to prevent circular import
        #TODO Remove the plot_func once fully tested!

        :return: Nothing. All values are stored in this object
        """

        if num_peaks_desired > MAX_PEAKS_TO_FIT:
            raise ValueError("fit - num_peaks_desired = {} exceeds max allowed {}".format(num_peaks_desired, MAX_PEAKS_TO_FIT))

        # The x values (i.e. predictors are the log dp values
        # The y values are the *filtered* clean concentration values
        xdata = self.get_log_dp_range()
        ydata = self._y_filtered
        ydata_smoothed = calc_moving_ave(ydata,3)
        xdata_width = xdata.max() - xdata.min()

        # y_gt_zero = ydata[(self._y_sel_good) & (ydata > 0)]
        # self.fit_weights = np.asarray([0.01 for _ in ydata])

        if verbose:
            print("Starting fit")
            print("xdata.shape = {}".format(xdata.shape))
            print("ydata.shape = {}".format(ydata.shape))
            print("xdata_width = {}".format(xdata_width))

        # Obtain a list of the indices of the peaks we expect to find in the data
        i_peaks = predict_peaks(ydata_smoothed, is_scan=True, verbose=verbose)
        self.num_peaks_predicted = len(i_peaks)

        # Now, go through each identified peak and use it to identify some good starting points for curve fitting the
        # gaussian
        p0_init = []
        min_bounds = []
        max_bounds = []
        for i in range(len(i_peaks)):
            init_amp = ydata[i_peaks[i]]
            min_amp = init_amp * 0.1
            max_amp = init_amp * 1.5

            init_mu = xdata[i_peaks[i]]
            min_mu = init_mu - xdata_width * 0.05
            max_mu = init_mu + xdata_width * 0.05

            init_sd = xdata_width * 0.05
            min_sd = xdata_width * 0.01
            max_sd = xdata_width * 0.20

            p0_init = p0_init + [init_amp,init_mu,init_sd]
            min_bounds = min_bounds + [min_amp, min_mu, min_sd]
            max_bounds = max_bounds + [max_amp, max_mu, max_sd]
            if i + 1 == num_peaks_desired:
                break
        bounds = (min_bounds, max_bounds)

        num_peaks_predicting = len(i_peaks)
        if num_peaks_predicting > num_peaks_desired:
            num_peaks_predicting = num_peaks_desired



        # Start with selecting all data
        sel = [True for i in range(xdata.shape[0])]

        is_done = False
        while not is_done:

            fit_func = get_gaussian_fit_func(num_peaks_predicting)

            if verbose:
                for peak in range(num_peaks_predicting):
                    print("p0_init = {}".format(p0_init[peak * 3:(peak + 1) * 3]))
                    print("min bounds = {}".format(bounds[0][peak * 3:(peak + 1) * 3]))
                    print("max bounds = {}".format(bounds[1][peak * 3:(peak + 1) * 3]))

            # Fit the desired number of peaks for this pass
            popt, pcov = scipy.optimize.curve_fit(
                fit_func,
                xdata[sel],
                ydata_smoothed[sel],
                p0=p0_init,
                bounds=bounds
            )
            # perr_gauss = np.sqrt(np.diag(pcov_gauss))

            # Create the peak results object
            if verbose:
                print("Predicting {} : parameters:".format(num_peaks_predicting))

            self.peak_fit_results = list()
            for i_peak in range(num_peaks_predicting):
                peak_fit_result = PeakFitResult()
                params = popt[i_peak * 3:(i_peak + 1) * 3]
                peak_fit_result.fit_params = params
                peak_fit_result.index = i_peak
                peak_fit_result.dp = np.exp(params[1])
                peak_fit_result.height = params[0]
                peak_fit_result.sd = np.exp(params[1] + params[2]) - peak_fit_result.dp  #TODO Verify this - this may not be right
                peak_fit_result.fwhh = peak_fit_result.sd * 2.3548 #TODO - Verify this - it may not be right
                peak_fit_result.growth_factor = 0 #TODO Finish growth factor calculation!
                peak_fit_result.kappa = 0 #TODO Finish kappa calculation!
                self.peak_fit_results.append(peak_fit_result)
                if verbose:
                    print(repr(peak_fit_result))

            self.total_fit_result = TotalFitResult()
            self.total_fit_result.predicted_peak_indices = i_peaks
            self.total_fit_result.num_peaks = num_peaks_desired
            self.total_fit_result.fit_params = popt
            self.total_fit_result.fit_values = list(map(lambda x: fit_func(x, *popt), xdata))
            self.total_fit_result.residuals = ydata - self.total_fit_result.fit_values
            self.total_fit_result.residuals_smoothed = calc_moving_ave(self.total_fit_result.residuals,3)
            # The indices of residual peaks is a lag value from the previous pass!
            self.total_fit_result.rmse = np.sqrt(np.sum(self.total_fit_result.residuals[self._y_sel_good] *
                                                        self.total_fit_result.residuals[self._y_sel_good]))
            # Durbin-Watson - a good test of fitness, measures the independence of the
            # residuals, or more specifically, there is no serial correlation.
            # Range is 0-4. A value of 2 is ideal
            self.total_fit_result.durbin_watson = durbin_watson(self.total_fit_result.residuals)

            # Compute E(residuals) i.e. the mean should be 0
            self.total_fit_result.residuals_mean = np.mean(self.total_fit_result.residuals)

            if verbose:
                print(repr(self.total_fit_result))

            if plot_steps:
                if verbose:
                    print("Generating plot...")
                # if ax_data is None:

                # Yeah, making the fig and gridspec part of the class, not a great idea, but good enough
                self.fig = plt.figure(figsize=(6, 4), dpi=100)
                self.gridspec = self.fig.add_gridspec(4, 1)

                ax_data = self.fig.add_subplot(self.gridspec[0:3, 0])
                ax_residuals = self.fig.add_subplot(self.gridspec[3, 0],
                                                    sharex=ax_data)

                plot_func(self,ax_data=ax_data,ax_residuals=ax_residuals)
                ax_data.annotate('test label',
                                 xy=(0.1, 0.8), xycoords='figure fraction', fontsize=15)
                ax_data.text(100, 1000, r'$\mu=100,\ \sigma=15$')
                plt.show()

            if num_peaks_predicting < num_peaks_desired:
                # If the user actually wants more peaks than were identified, then
                # lets use the residual curve to determine ideal locations
                i_residual_peaks = predict_peaks(self.total_fit_result.residuals_smoothed,
                                                 is_scan=False,
                                                 verbose=verbose)

                # Sometimes the residual can measure a large at the tails of
                # the gaussian, when the acutal data is zero
                is_good_peak = False
                for i_pk in i_residual_peaks:
                    if ydata[i_pk] > 0:
                        is_good_peak = True
                        break

                # IF there were peaks identified, let's use them!
                if is_good_peak:
                    init_amp = ydata[i_pk]
                    min_amp = init_amp * 0.1
                    max_amp = init_amp * 1.5

                    init_mu = xdata[i_pk]
                    min_mu = init_mu - xdata_width * 0.25
                    max_mu = init_mu + xdata_width * 0.25

                    init_sd = xdata_width * 0.05
                    min_sd = xdata_width * 0.01
                    max_sd = xdata_width * 0.20

                    p0_init = p0_init + [init_amp, init_mu, init_sd]
                    min_bounds = min_bounds + [min_amp, min_mu, min_sd]
                    max_bounds = max_bounds + [max_amp, max_mu, max_sd]
                    bounds = (min_bounds, max_bounds)

                else:
                    print("CRAP! Sorry! Could not find additional peaks!")
                    init_amp = ydata[i_peaks[0]]
                    min_amp = ydata.max() * 0.005
                    max_amp = ydata.max() * 1.25

                    init_mu = xdata[i_peaks[0]]
                    # TODO - Need to figure out the appropriate peak range in this case
                    min_mu = xdata[INDEX_OF_PEAK_BOUNDS]
                    max_mu = xdata[-(INDEX_OF_PEAK_BOUNDS+1)]

                    init_sd = xdata_width * 0.05
                    min_sd = xdata_width * 0.01
                    max_sd = xdata_width * 0.25

                    p0_init = p0_init + [init_amp, init_mu, init_sd]
                    min_bounds = min_bounds + [min_amp, min_mu, min_sd]
                    max_bounds = max_bounds + [max_amp, max_mu, max_sd]
                    bounds = (min_bounds, max_bounds)

                num_peaks_predicting = num_peaks_predicting + 1
            else:
                is_done = True
            # Now, this is the tricky part. Here, we carefully narrow in on the correct
            # gaussians by eliminating data that is outside of some fraction of standard
            # deviations for each curve
            # sel = [False for i in range(xdata.shape[0])]

            # For each peak select the data around it to use for the next iteration
            # for peak in range(num_peaks_predicting):
            #     x_mean_est = popt[peak * 3 + 1]
            #     x_sd_est = popt[peak * 3 + 2]
            #
            #     # Now, we need to determine how much data around the sd we want
            #     #                x_sd_factor = 1
            #     x_sd_factor = 2 / (step + 1)
            #
            #     # Find the min and max around the mean, and select that data for next iteration
            #     min_x = x_mean_est - x_sd_est * x_sd_factor
            #     max_x = x_mean_est + x_sd_est * x_sd_factor
            #     sel_peak = (xdata >= min_x) & (xdata <= max_x)
            #
            #     # Select it!
            #     sel = sel | sel_peak

            # Set the new parameters
            # p0_init = popt

        # Compute the RMSE near peaks
        # sel_near_peak = [False for i in range(xdata.shape[0])]
        # for peak in range(num_peaks_desired):
        #     params = popt[peak * 3:(peak + 1) * 3]
        #     sel_near_peak |= (xdata > params[1] - params[2]) & (xdata < params[1] + params[2])
        #     if verbose:
        #         print(sel_near_peak)
        #
        # self.fit_rmse_near_peaks = np.sqrt(np.sum(self.fit_residuals[sel_near_peak] * self.fit_residuals[sel_near_peak]))
        #
        # if verbose:
        #     print("RMSE = {}".format(self.fit_result_rmse))
        #     print("Durbin-Watson = {}".format(dw))
        #     print("narrow RMSE = {}".format(self.fit_rmse_near_peaks))

        # return popt, pcov
        # TODO - Temporary - add the fit results from the current scan...

        return


    # def get_fit_peak_dp(self):
    #     """
    #     :return:         Return a list of the fitted dp values
    #     """
    #     sel = np.array(list(range(1,1+3*(self.fit_num_peaks-1)+1,3)))
    #     x = np.exp(self.fit_peak_params[sel])
    #     return x


def get_gaussian_fit_func(num_peaks):
    """
    Return the correct fit function depending on the number of gaussians you
    are trying to fit
    """
    if num_peaks == 1:
        fit_func = _1gaussian
    elif num_peaks == 2:
        fit_func = _2gaussian
    elif num_peaks == 3:
        fit_func = _3gaussian
    elif num_peaks == 4:
        fit_func = _4gaussian
    elif num_peaks == 5:
        fit_func = _5gaussian
    else:
        fit_func = None
    return fit_func


def calc_moving_ave(x, w: int):
    """
    Compute the moving average of a series

    :param x: The data
    :param w: The window size for computing the average

    :returns: The moving averaged x using a windows size of w, padded
              with zeros to make it the same length
    """

    if w % 2 == 0:
        raise ValueError("calc_moving_ave parameter w must be odd")

    x = np.convolve(x, np.ones(w), 'valid') / w
    pad = (w-1) // 2
    x = np.append(np.zeros(pad), x)
    x = np.append(x, np.zeros(pad))
    return x


def predict_peaks(data, is_scan: bool, verbose=False):
    """
    Given a signal, predict the indices of the peaks. The hard work of this method is
    done by `scipy.signal.find_peaks`.

    :param data: the data (either scan or residual)
    :param is_scan: Is this scan data or residual data?
    :param verbose: [Optional, default=False] do we output some debug info while working?
    :returns: a list of indicies locating where the peaks in the signal are, sorted from the
    strongest peak to the weakest
    """

    # data = np.convolve(data, np.ones(3), 'valid') / 3
    # data = np.append([0], data)
    # data = np.append(data, [0])

    x = data

    # Vertical distance of the peak to neighbor samples
    # NOTE - changed 20221021 - it was threshold = (0, (x.max() - x.min()) / 4)
    # But for very thin tall peaks with very few points, the threshold was too tight.
    threshold = (0, (x.max() - x.min()) / 2)
    # distance to neighbor peaks in samples
    distance = 10
    # width of the peak in samples
    width = 1
    # Relative height at which width is measured as a percentage of
    # its prominence
    rel_height = 0.2
    # prominence of the peak
    # - how much a peak stands out from the surrounding baseline
    #   of the signal and is defined as the vertical distance between
    #   the peak and its lowest contour line
    prominence = ((x.max() - x.min()) / 10,
                  (x.max() - x.min()))
    if not is_scan:
        x = np.multiply(x, -1.0)
        #distance=5
        width=3
        rel_height= 0.25
        prominence = ((x.max() - x.min()) / 20,
                      (x.max() - x.min()))

    i_pk, other = scipy.signal.find_peaks(x,
                                          threshold=threshold,
                                          distance=distance,
                                          width=width,
                                          rel_height=rel_height,
                                          prominence=prominence
                                          )

    if verbose:
        print("find_peaks found {} peaks".format(len(i_pk)))

    #widths, _ = peak_widths(data,i_pk,rel_height=0.1)
    # Sort from the highest/strongest peak to the lowest/weakest
    if len(i_pk) > 0:
        i_pk = sorted(i_pk, key=lambda i: x[i], reverse=True)
        i_pk_good = []
        for i in i_pk:
            if i >= INDEX_OF_PEAK_BOUNDS and i <= len(x) - 1 - INDEX_OF_PEAK_BOUNDS:
                i_pk_good.append(i)
        return i_pk_good
    else:
        return []

    return i_pk
