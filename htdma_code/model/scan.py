"""
This class represents a single Scan from a run. This code will handle
everything related to one scan, including curve fitting.



Let's recall the standard normal distribution as defined by the quintessential probability density function:
- https://en.wikipedia.org/wiki/Normal_distribution

- $f(x) = \frac{1}{\sigma \sqrt{2 \pi}}e^{-\frac{1}{2}(\frac{x - \mu}{\sigma})^2}$

I'm following lots of ideas online of basic gaussian curve fits

- http://www.emilygraceripka.com/blog/16

"""

import numpy as np
import pandas as pd
from statsmodels.stats.stattools import durbin_watson
import scipy
import scipy.signal
import scipy.optimize

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

class Scan:
    """
    Scan encapsulates a single scan of data

    Attributes:
        -
    """
    def __init__(self, df: pd.DataFrame, num_dp_values: int):
        """
        This function is passed a single scan column from the time
        stamp right through the end of the column

        :param df: A data frame representing all row data for a single scan
        :param num_dp_values: number of dp values in the scan
        """

        self.num_scan_rows = num_dp_values

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
        self.num_peaks_found = None # Number of peaks found by find_peaks
        self.fit_params = None      # Model parameters found by curve fit
        self.fit_values = None      # Fitted values
        self.fit_residuals = None   # Residuals between fit and raw values
        self.fit_rmse = None        # RMSE
        self.fit_num_peaks = None   # The number of peaks identified for best fit

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

    def fit(self,num_peaks,verbose = False, plot_steps = False, ax_data = None, ax_residuals = None):
        """
        This is the mother function that performs the curve fit. The results of the fit
        are stored in this class. Specifically:

        self.fit_params
        self.fit_values
        self.fit_residuals
        self.fit_rmse
        self.num_peaks_found

        TODO - add the ability to autodetect the number of peaks
        TODO - Improve the fitting to use weights

        :param num_peaks: For the time, the user must specify the number of peaks
        expected in the data.
        :param verbose: print out info while doing the fit?
        :param plot_steps: plot the fit after each step?
        :return: Nothing. All values are stored in the object, including

        """

        if num_peaks > MAX_PEAKS_TO_FIT:
            raise ValueError("fit - num_peaks = {} exceeds max allowed {}".format(num_peaks,MAX_PEAKS_TO_FIT))

        # The x values (i.e. predictors are the log dp values
        # The y values are the *filtered* clean concentration values
        xdata = self.get_log_dp_range()
        ydata = self._y_filtered
        xdata_width = xdata.max() - xdata.min()

        # TODO - delete this test
        # print("WARNING! Hard htdma_code filter log_dp < 4")
        # sel = xdata < 4.0
        # ydata[sel] = 0.0

        y_gt_zero = ydata[(self._y_sel_good) & (ydata > 0)]
        #self.fit_weights = np.asarray([0.01 for _ in ydata])

        if verbose:
            print("Starting fit")
            print("xdata.shape = {}".format(xdata.shape))
            print("ydata.shape = {}".format(ydata.shape))
            print("xdata_width = {}".format(xdata_width))


        # i_pk = scipy.signal.find_peaks_cwt(ydata,
        #                                    widths=range(3,10))
        # DX = (np.max(x) - np.min(x)) / float(Npks)  # starting guess for component width
        # guess = np.ravel([[x[i], y[i], DX] for i in i_pk])  # starting guess for (x, amp, width) for each component


        i_pk, _ = scipy.signal.find_peaks(ydata,
                                       distance=10,
                                       width=1,
                                       prominence=ydata.max()/20)

        self.num_peaks_found = len(i_pk)

        if verbose:
            print("find_peaks found {} peaks".format(len(i_pk)))

        # Sort the peak from highest to lowest
        i_pk = sorted(i_pk,key = lambda x : ydata[x],reverse=True)

        p0_init = []
        min_bounds = []
        max_bounds = []
        for i in range(len(i_pk)):
            if i == num_peaks:
                break

            init_amp = ydata[i_pk[i]]
            min_amp = init_amp * 0.1
            max_amp = init_amp * 1.5

            init_mu = xdata[i_pk[i]]
            min_mu = init_mu - xdata_width * 0.05
            max_mu = init_mu + xdata_width * 0.05

            init_sd = xdata_width * 0.05
            min_sd = xdata_width * 0.01
            max_sd = xdata_width * 0.1

            p0_init = p0_init + [init_amp,init_mu,init_sd]
            min_bounds = min_bounds + [min_amp, min_mu, min_sd]
            max_bounds = max_bounds + [max_amp, max_mu, max_sd]
        bounds = (min_bounds, max_bounds)

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

        if verbose:
            for peak in range(num_peaks):
                print("p0_init = {}".format(p0_init[peak*3:(peak+1)*3]))
                print("min bounds = {}".format(bounds[0][peak*3:(peak+1)*3]))
                print("max bounds = {}".format(bounds[1][peak*3:(peak+1)*3]))

        # Start with selecting all data
        sel = [True for i in range(xdata.shape[0])]

        for step in range(NUM_FIT_PASSES):

            popt, pcov = scipy.optimize.curve_fit(
                fit_func,
                xdata[sel],
                ydata[sel],
                p0=p0_init,
                bounds=bounds
            )
            # perr_gauss = np.sqrt(np.diag(pcov_gauss))

            if verbose:
                print("Pass {} : parameters:".format(step + 1))
                for peak in range(num_peaks):
                    print("Peak: {}".format(peak+1))
                    params = popt[peak*3:(peak+1)*3]
                    print("amp: {:.1f}".format(params[0]))
                    print("mu: {:.3f}".format(params[1]))
                    print("sd: {:.3f}".format(params[2]))

            # Generate fit data
            y_fit = list(map(lambda x: fit_func(x, *popt), xdata))

            # Store the fit values and their residuals
            self.fit_num_peaks = num_peaks
            self.fit_params = popt
            self.fit_values = y_fit
            self.fit_residuals = ydata - y_fit
            self.fit_rmse = np.sqrt(np.sum(self.fit_residuals[self._y_sel_good] *
                                           self.fit_residuals[self._y_sel_good]))

            dw = durbin_watson(self.fit_residuals)

            # Compute the RMSE near peaks
            sel_near_peak = [False for i in range(xdata.shape[0])]
            for peak in range(num_peaks):
                params = popt[peak * 3:(peak + 1) * 3]
                sel_near_peak |= (xdata > params[1] - params[2]) & (xdata < params[1] + params[2])
                if verbose:
                    print(sel_near_peak)

            self.fit_rmse_near_peaks = np.sqrt(np.sum(self.fit_residuals[sel_near_peak] * self.fit_residuals[sel_near_peak]))

            if verbose:
                print("RMSE = {}".format(self.fit_rmse))
                print("Durbin-Watson = {}".format(dw))
                print("narrow RMSE = {}".format(self.fit_rmse_near_peaks))

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

                self.plot(ax_data=ax_data,ax_residuals=ax_residuals)
                ax_data.annotate('test label',
                            xy=(0.1, 0.8), xycoords='figure fraction', fontsize=15)
                ax_data.text(100, 1000, r'$\mu=100,\ \sigma=15$')
                plt.show()

            # Now, this is the tricky part. Here, we carefully narrow in on the correct
            # gaussians by eliminating data that is outside of some fraction of standard
            # deviations for each curve
            sel = [False for i in range(xdata.shape[0])]

            # For each peak select the data around it to use for the next iteration
            for peak in range(num_peaks):
                x_mean_est = popt[peak * 3 + 1]
                x_sd_est = popt[peak * 3 + 2]

                # Now, we need to determine how much data around the sd we want
#                x_sd_factor = 1
                x_sd_factor = 2 / (step + 1)

                # Find the min and max around the mean, and select that data for next iteration
                min_x = x_mean_est - x_sd_est * x_sd_factor
                max_x = x_mean_est + x_sd_est * x_sd_factor
                sel_peak = (xdata >= min_x) & (xdata <= max_x)

                # Select it!
                sel = sel | sel_peak

            # Set the new parameters
            p0_init = popt

        # return popt, pcov
        return

    def get_fit_peak_dp(self):
        """
        :return:         Return a list of the fitted dp values
        """
        print(self.fit_num_peaks)
        sel = np.array(list(range(1,1+3*(self.fit_num_peaks-1)+1,3)))
        x = np.exp(self.fit_params[sel])
        return x


    def plot(self, ax_data: plt.Axes, ax_residuals: plt.Axes):
        """
        Create a plot of the raw data and fitted data in ax_data,
        and the residuals resulting from the fit in ax_residuals. If the user
        does not want to plot residuals, OR if a fit has not been completed,
        then the residuals are not plotted

        :param ax_data: The Axes object to plot the data in
        :param ax_residuals: The Axes object to plot the residuals in, or None
        if no residuals are plotted.
        """

        # fig = plt.figure(figsize=(10,8))
        # ax = fig.add_gridspec(4,1)
        # ax_data = fig.add_subplot(ax[0:3,0])
        # ax_residuals = fig.add_subplot(ax[3,0])

        #xdata = self.get_log_dp_range()
        xdata = self.get_dp_range()
        ydata = self.get_values()

        # Plot actual data
        ax_data.plot(xdata,ydata, "ro")
        #ax_data.set_ylabel("conc",family="serif",  fontsize=12)
        ax_data.set_ylabel("conc", fontsize=20)
        ax_data.grid(True)
        ax_data.set_xscale("log")
        ax_data.set_xticks([10,50] + list(range(100,1000,100)))
        ax_data.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())

        # Plot the curve fit... if a fit was completed
        if self.fit_values:
            ax_data.plot(xdata,self.fit_values, 'k--')

            #y_fit = list(map(lambda x: fit_func(x, *popt), xdata))

            # Let's separate the peaks
            for peak in range(self.fit_num_peaks):
                gauss_params = self.fit_params[peak*3:(peak+1)*3]
                gauss_fit = _1gaussian(self.get_log_dp_range(), *gauss_params)
                color = "gbmcy"[peak]
                ax_data.plot(xdata,gauss_fit,color)

            ax_residuals.plot(xdata[self._y_sel_good], self.fit_residuals[self._y_sel_good], "bo")
            ax_residuals.plot(xdata[np.logical_not(self._y_sel_good)],
                     self.fit_residuals[np.logical_not(self._y_sel_good)],
                     "k.")
            ax_residuals.plot(xdata, np.zeros(xdata.shape[0]))
            ax_residuals.set_xlabel("dp", fontsize=15)
            ax_residuals.set_ylabel("residuals", fontsize=15)
            ax_residuals.grid(True)

        ax_data.legend(loc="best")

        # fig.tight_layout()
        #
        # return fig, ax
