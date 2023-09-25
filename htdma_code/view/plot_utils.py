import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt

from htdma_code.model.scan import Scan, _1gaussian, predict_peaks


def plot_scan_and_residuals(scan: Scan,
                            ax_data: plt.Axes,
                            ax_residuals: plt.Axes):
    """
    Create a plot of the raw data and fitted data in ax_data,
    and the residuals resulting from the fit in ax_residuals. If the user
    does not want to plot residuals, OR if a fit has not been completed,
    then the residuals are not plotted

    :param scan: The Scan object that contains the data to be plotted
    :param ax_data: The Axes object to plot the data in
    :param ax_residuals: The Axes object to plot the residuals in, or None
    if no residuals are plotted.
    """

    # fig = plt.figure(figsize=(10,8))
    # ax = fig.add_gridspec(4,1)
    # ax_data = fig.add_subplot(ax[0:3,0])
    # ax_residuals = fig.add_subplot(ax[3,0])

    #xdata = self.model.get_log_dp_range()
    xdata = scan.get_dp_range()
    ydata = scan.get_values()

    # Plot actual data
    ax_data.plot(xdata,ydata, "ro")
    #ax_data.set_ylabel("conc",family="serif",  fontsize=12)
    ax_data.set_ylabel("conc (#/cm^3)", fontsize=20)
    ax_data.grid(True)
    ax_data.set_xscale("log")
    ax_data.set_xticks([10,50] + list(range(100,1000,100)))
    ax_data.get_xaxis().set_major_formatter(mpl.ticker.ScalarFormatter())

    total_fit_result = scan.total_fit_result
    peak_fit_results = scan.peak_fit_results
    # Plot the curve fit... if a fit was completed
    if total_fit_result:
        # Let's show those initial peak identified
        if len(total_fit_result.predicted_peak_indices) > 0:
            ax_data.plot(xdata[total_fit_result.predicted_peak_indices],
                            ydata[total_fit_result.predicted_peak_indices],
                            'k*')
        ax_data.plot(xdata,total_fit_result.fit_values, 'k--')

        # Let's separate the peaks
        for peak in peak_fit_results:
            gauss_fit = _1gaussian(scan.get_log_dp_range(), *peak.fit_params)
            color = "gbmcy"[peak.index]
            ax_data.plot(xdata,gauss_fit,color)

        sel = scan._y_sel_good
        ax_residuals.plot(xdata[sel],
                          total_fit_result.residuals[sel], "bo")
        ax_residuals.plot(xdata[np.logical_not(sel)],
                          total_fit_result.residuals[np.logical_not(sel)],
                          "k.")
        ax_residuals.plot(xdata, np.zeros(xdata.shape[0]))
        i_residual_peaks = predict_peaks(total_fit_result.residuals,
                                         is_scan=False,
                                         verbose=False)

        if len(i_residual_peaks) > 0:
            ax_residuals.plot(xdata[i_residual_peaks],
                            total_fit_result.residuals[i_residual_peaks],
                            'k*')

        ax_residuals.set_xlabel("dp (nm)", fontsize=15)
        ax_residuals.set_ylabel("residuals", fontsize=15)
        ax_residuals.grid(True)

    ax_data.legend(loc="best")

    # fig.tight_layout()
    #
    # return fig, ax

