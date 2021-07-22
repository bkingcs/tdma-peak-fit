"""
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

class Sample:
    """
    Sample encapsulates a single sample of data and its parameters
    """
    def __init__(self, df: pd.DataFrame, num_dp_values: int):
        """
        This function is passed a single sample column from the time
        stamp right through the end of the column

        :param df: A data frame representing all row data for a single sample
        :param num_dp_values: number of dp values in the sample
        """
        self.sample_num = int(df.columns[0])
        self.time_stamp = df.iat[0,0]

        self.num_sample_rows = num_dp_values

        # Let's keep an internal dataframe of the data, for now...
        self._df_data = df.iloc[1:1+self.num_sample_rows,[0]].copy()
        self._df_data.index = self._df_data.index.astype(float)
        self._df_data = self._df_data.astype(float)

        # Extract out numpy arrays of the data for speed
        self.dp_range = self._df_data.index.to_numpy()
        self.log_dp_range = np.log(self.dp_range)
        self.raw_values = self._df_data.iloc[:,0].to_numpy()

        # Extract out the other parameters
        self.scan_up_time = float(df.iat[self.num_sample_rows+1,0])
        self.scan_down_time = float(df.iat[self.num_sample_rows+2,0])
        self.q_sh_lpm = float(df.iat[self.num_sample_rows + 6, 0])
        self.q_aIn_lpm = float(df.iat[self.num_sample_rows + 7, 0])
        self.q_aOut_lpm = float(df.iat[self.num_sample_rows + 8, 0])
        self.low_V = float(df.iat[self.num_sample_rows+10,0])
        self.high_V = float(df.iat[self.num_sample_rows+11,0])
        self.status = df.iat[self.num_sample_rows+16,0]

        # Validate the setup. Check whether the setup is symmetric or not
        self.is_symmetric = True
        self.q_excess_lpm = self.q_sh_lpm
        if self.q_aIn_lpm != self.q_aOut_lpm:
            self.is_symmetric = False
            self.q_excess_lpm = self.q_sh_lpm + self.q_aIn_lpm - self.q_aOut_lpm

        # Curve fit parameters and constants
        self._MIN_GOOD_WINDOW_SIZE = 5
        self._NUM_FIT_PASSES = 6

        # Preprocess / clean data to prepare for curve fit
        self._y_filtered, self._y_sel_good = self._filter_bad_values()
        self._yfit = None
        self._y_weights = None

        # Parameters that are set by the fit function
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

        :return: The fitlered values, and the boolean selection array indicating
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
                    if count_good_channels < self._MIN_GOOD_WINDOW_SIZE:
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
        s = "sample #: {}\n".format(self.sample_num)
        s += "dp range: {}\n".format(repr(self.dp_range))
        s += "values: {}\n".format(repr(self.raw_values))
        s += "scan up (sec): {}\n".format(self.scan_up_time)
        s += "scan down (sec): {}\n".format(self.scan_down_time)
        s += "low V: {}\n".format(self.low_V)
        s += "high V: {}\n".format(self.high_V)
        s += "q_sh_lpm (lpm): {}\n".format(self.q_sh_lpm)
        s += "q_aIn_lpm (polydisperse) (lpm): {}\n".format(self.q_aIn_lpm)
        s += "q_aOut_lpm (monodisperse) (lpm): {}\n".format(self.q_aOut_lpm)
        s += "STATUS: {}\n".format(self.status)

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

    def fit(self,num_peaks,verbose = False, plot_steps = False):
        """
        This is the mother function that performs the curve fit. The results of the fit
        are stored in this class. Specifically:

        self.fit_params
        self.fit_values
        self.fit_residuals
        self.fit_rmse

        TODO - add the ability to autodetect the number of peaks
        TODO - Improve the fitting to use weights

        :param num_peaks: For the time, the user must specify the number of peaks
        expected in the data.
        :param verbose: print out info while doing the fit?
        :param plot_steps: plot the fit after each step?
        :return: Nothing. All values are stored in the object, including

        """

        # The x values (i.e. predictors are the log dp values
        # The y values are the *filtered* clean concentration values
        xdata = self.get_log_dp_range()
        ydata = self._y_filtered

        # TODO - delete this test
        # print("WARNING! Hard code filter log_dp < 4")
        # sel = xdata < 4.0
        # ydata[sel] = 0.0

        y_gt_zero = ydata[(self._y_sel_good) & (ydata > 0)]
        #self.fit_weights = np.asarray([0.01 for _ in ydata])

        if verbose:
            print("Starting fit")
            print("xdata.shape = {}".format(xdata.shape))
            print("ydata.shape = {}".format(ydata.shape))

        # Set up initial starting points for our parameters
        # initial parameters to use
        p0_init = [y_gt_zero.mean() * .5,
                   xdata.mean(),
                   (xdata.max() - xdata.min()) * 0.05]*num_peaks
        bounds = ([y_gt_zero.mean() * 0.1,  # min amp
                   xdata.min(),  # min mu
                   (xdata.max() - xdata.min()) * 0.01] * num_peaks,  # min sd
                  [y_gt_zero.max() * 2,  # max amp
                   xdata.max(),  # max mu
                   (xdata.max() - xdata.min()) * 0.2] * num_peaks)  # max sd

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

        for step in range(self._NUM_FIT_PASSES):

            popt, pcov = scipy.optimize.curve_fit(
                fit_func,
                xdata[sel],
                ydata[sel],
                p0=p0_init,
                bounds=bounds
            )
            # perr_gauss = np.sqrt(np.diag(pcov_gauss))

            # Generate fit data
            if verbose:
                print("Pass {} : parameters:".format(step + 1))
                for peak in range(num_peaks):
                    print("Peak: {}".format(peak+1))
                    params = popt[peak*3:(peak+1)*3]
                    print("amp: {:.1f}".format(params[0]))
                    print("mu: {:.3f}".format(params[1]))
                    print("sd: {:.3f}".format(params[2]))

            y_fit = list(map(lambda x: fit_func(x, *popt), xdata))

            # Store the fit values and their residuals
            self.fit_num_peaks = num_peaks
            self.fit_params = popt
            self.fit_values = y_fit
            self.fit_residuals = ydata - y_fit
            self.fit_rmse = np.sqrt(np.sum(self.fit_residuals[self._y_sel_good] *
                                           self.fit_residuals[self._y_sel_good]))

            dw = durbin_watson(self.fit_residuals)

            if verbose:
                print("RMSE = {}".format(self.fit_rmse))
                print("Durbin-Watson = {}".format(dw))

            if plot_steps:
                fig, ax = self.plot_fit()
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



    def plot_fit(self):
        """
        Create a plot of the raw data and fitted data
        :return: Figure, Axes
        """
        fig = plt.figure(figsize=(10,8))
        ax = fig.add_gridspec(4,1)
        ax1 = fig.add_subplot(ax[0:3,0])
        ax2 = fig.add_subplot(ax[3,0])

        xdata = self.get_log_dp_range()
        ydata = self.get_values()

        # Plot actual data
        ax1.plot(xdata,ydata, "ro")

        # Plot the curve fit
        ax1.plot(xdata,self.fit_values, 'k--')

        # Let's separate the peaks
        for peak in range(self.fit_num_peaks):
            gauss_params = self.fit_params[peak*3:(peak+1)*3]
            gauss_fit = _1gaussian(xdata, *gauss_params)
            color = "gbmcy"[peak]
            ax1.plot(xdata,gauss_fit,color)

        #ax.set_xscale('log')
        ax2.plot(xdata[self._y_sel_good], self.fit_residuals[self._y_sel_good], "bo")
        ax2.plot(xdata[np.logical_not(self._y_sel_good)],
                 self.fit_residuals[np.logical_not(self._y_sel_good)],
                 "k.")
        ax2.plot(xdata, np.zeros(xdata.shape[0]))
        ax2.set_xlabel("log dp",family="serif",  fontsize=12)
        ax1.set_ylabel("conc",family="serif",  fontsize=12)
        ax2.set_ylabel("residuals")

        ax1.legend(loc="best")

        fig.tight_layout()

        return fig, ax
