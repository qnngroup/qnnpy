# Written by Adam McCaughan Jan 17, 2014
# Run add_path.py first

import os
from datetime import datetime

# import cPickle as pickle
import matplotlib.cm as cm
import numpy as np
import scipy.io
from matplotlib import pyplot as plt


def save_xy_vs_param(
    X,
    Y,
    P,
    xname="x",
    yname="y",
    pname="p",
    test_type="Y Measurement",
    test_name="Test01",
    xlabel="amps",
    ylabel="volts",
    plabel="farads",
    title="",
    legend=False,
    xscale=1,
    yscale=1,
    pscale=1,
    comments="",
    filedir="",
    display_plot=False,
    zip_file=True,
):
    """Save list-of-lists X and Y data, along with list P (parameter) as MATLAB .mat file and Python .pickle file
    and additionally zips those .mat and .pickle files together with a .png of the graph
    """
    X = np.array(X)
    Y = np.array(Y)
    P = np.array(P)
    data_dict = {xname: X, yname: Y, pname: P, "comments": comments}
    time_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_name = "%s %s %s" % (test_type, time_str, test_name)
    file_path = os.path.join(filedir, file_name)

    # Save data in MATLAB and pickle formats
    scipy.io.savemat(file_path + ".mat", mdict=data_dict)
    # f = open(file_path + '.pickle', 'wb'); pickle.dump(data_dict, f); f.close()

    # Plot data
    if X.ndim == 1:
        plt.plot(X * xscale, Y * yscale)
    elif X.ndim == 2:
        mycm = cm.winter
        cm_indices = np.linspace(0, mycm.N * 0.8, len(X))
        for n in range(len(X)):
            plt.plot(
                X[n] * xscale,
                Y[n] * yscale,
                label="%0.3f %s" % (P[n] * pscale, plabel),
                c=mycm(int(cm_indices[n])),
            )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    if legend is True:
        plt.legend(loc="best")
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(
        False
    )  # Remvoes relative shift on graph
    plt.savefig(file_path + ".png")

    print("Saving data and figure with filename: %s" % file_name)
    # zf = zipfile.ZipFile(file_path + '.zip', 'w')
    # for name in ['.pickle', '.mat', '.png']:
    #    zf.write(file_path + name, arcname = file_name + name, compress_type = zipfile.ZIP_DEFLATED)

    if display_plot is True:
        plt.show()
    else:
        plt.close()
    return file_path


def save_x_vs_param(
    X,
    P,
    xname="x",
    pname="p",
    test_type="X Measurement",
    test_name="Test01",
    comments="",
    filedir="",
    zip_file=True,
):
    """Save list-of-lists X data, along with list P (parameter) as MATLAB .mat file and Python .pickle file
    and additionally zips those .mat and .pickle files together with a .png of the graph
    """
    data_dict = {xname: X, pname: P, "comments": comments}
    time_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_name = "%s %s %s" % (test_type, time_str, test_name)
    file_path = os.path.join(filedir, file_name)

    # Save data in MATLAB and pickle formats
    scipy.io.savemat(file_path + ".mat", mdict=data_dict)
    # f = open(file_path + '.pickle', 'wb'); pickle.dump(data_dict, f); f.close()

    print("Saving data and figure with filename: %s" % file_name)
    # zf = zipfile.ZipFile(file_path + '.zip', 'w')
    # for name in ['.pickle', '.mat']:
    #    zf.write(file_path + name, arcname = file_name + name, compress_type = zipfile.ZIP_DEFLATED)

    return (file_path, file_name)


def save_data_dict(
    data_dict, test_type="X Measurement", test_name="Test01", filedir="", zip_file=True
):
    """Directly input the data dictionary that scipy.io.savemat wants, and automatically zip the pickle
    and matlab file up"""
    time_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    file_name = "%s %s %s" % (test_type, time_str, test_name)
    file_path = os.path.join(filedir, file_name)

    # Save data in MATLAB and pickle formats
    scipy.io.savemat(file_path + ".mat", mdict=data_dict)
    # f = open(file_path + '.pickle', 'wb'); pickle.dump(data_dict, f); f.close()

    print("Saving data and figure with filename: %s" % file_name)
    # zf = zipfile.ZipFile(file_path + '.zip', 'w')
    # for name in ['.mat']:
    #     # zf.write(file_path + name, arcname = file_name + name, compress_type = zipfile.ZIP_DEFLATED)
    #     zf.write(file_path + name, arcname = file_name + name)

    return (file_path, file_name)


# X = []
# Y = []
# P = []
# for n in range(10):
#     X.append(np.linspace(0,10,100))
#     Y.append(np.random.rand(100) + n)
#     P.append(n)


# fn = save_xy_vs_param(X, Y, P, xname = 'f', yname = 'output', pname = 'shift',
#                         test_type = 'ZZZ Measurement', test_name = 'Test01',
#                         xlabel = 'Frequency (GHz)', ylabel = 'Whatup', title = 'Hey there',
#                         filedir = '/Users/amcc/Documents/MATLAB',
#                         legend = True, display_plot = True)
