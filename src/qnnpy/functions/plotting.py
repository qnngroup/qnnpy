import datetime

import scipy.io
from matplotlib import pyplot as plt


def save_plot(
    x,
    y,
    filename,
    xlabel="",
    ylabel="",
    title="",
    legend=None,
    prepend_time=True,
    save_plot=True,
    show_plot=False,
):
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename = time_str + " " + filename
    scipy.io.savemat(filename + ".mat", mdict={"x": x, "y": y})

    plt.plot(x, y, "-o")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if legend is not None:
        plt.legend(title)
    plt.savefig(filename)
    if show_plot is True:
        plt.show()
    plt.close()


def save_multi_plots(
    x1,
    y1,
    x2,
    y2,
    filename,
    xlabel="",
    ylabel="",
    title="",
    legend=None,
    prepend_time=True,
    save_plot=True,
    show_plot=False,
):
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename = time_str + " " + filename
    scipy.io.savemat(filename + ".mat", mdict={"x1": x1, "y1": y1, "x2": x2, "y2": y2})

    plt.plot(x1, y1, "-bo")
    plt.plot(x2, y2, "-ro")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if legend is not None:
        plt.legend(legend)
    plt.savefig(filename)
    if show_plot is True:
        plt.show()
    plt.close()
