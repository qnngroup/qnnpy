# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 09:31:52 2020

@author: omedeiro

This script is designed to extract the temperature data from ICE oxford
generated log files. Previous IoT efforts failed due to high memory consumption
and difficulity interfacing (caused by ICE software) with the temperature
controller


"""

import datetime
import os
import sys

import numpy as np
import scipy.io
from matplotlib import pyplot as plt

path = r"S:\SC\InstrumentLogging\Cryogenics\Ice\_copy_of_ice_log\Results"


# %%
""" Plot all TIME-TEMP data"""


def date_plot(path, date_start, date_end=datetime.date.today().isoformat(), plot=None):
    sys.path.append(path)
    folder_list = os.listdir(path)
    folder_list.sort()

    ds = datetime.datetime.strptime(date_start, "%Y-%m-%d")
    de = datetime.datetime.strptime(date_end, "%Y-%m-%d")

    """ Convert strings to dates for boolean condition """
    date_list = [
        datetime.datetime.strptime(folder_list[i], "%Y-%m-%d")
        for i in range(len(folder_list))
        if datetime.datetime.strptime(folder_list[i], "%Y-%m-%d") > ds
        and datetime.datetime.strptime(folder_list[i], "%Y-%m-%d") < de
    ]

    """ Convert dates back to strings """
    date_list_str = [d.strftime("%Y-%m-%d") for d in date_list]

    x = []
    y = []
    for r in date_list_str:
        new_path = os.path.join(path, r, r + ".log")
        f = open(new_path)
        lines = f.readlines()
        for line in lines:
            cells = line.split(",")
            date = datetime.datetime.strptime(cells[3], "%m/%d/%Y %I:%M:%S %p")
            data = [float(cells[4]), float(cells[5]), float(cells[6]), float(cells[7])]

            if data[0] < 290:
                x.append(date)
                y.append(data)
    if plot:
        plt.plot(x, y, marker="o", ls="None")
        plt.legend(["Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4"], loc="upper right")

    return x, y


# %%
"""nice single line command """
# time_diff = [td.total_seconds() for td in np.diff(x) if td.total_seconds()>30]


def save_cycle(x, y):
    """
    This function takes in datetime.datetime and temperature data (generally
    created using date_plot()) and extracts each complete cooldown/warmup cycle.
    """

    """ Extract START-END points of temperature sweeps """
    time_diff_index = []
    dx = np.diff(x)
    for t in range(len(np.diff(x))):
        td = dx[t].total_seconds()
        if td > 10000:  # finds when the log was off.
            time_diff_index.append(t)
            print(x[t])

    """ Filter lists such that each sweep has High temp and Low temp"""
    trace_list = []
    for i in range(len(time_diff_index) - 1):
        temp = y[time_diff_index[i] + 1 : time_diff_index[i + 1] + 1]
        temp_array = np.asarray(temp, dtype=np.float64)
        if (
            temp_array[0, 0] > 150
            and temp_array[-1, 0] > 150
            and np.min(temp_array[:, 0]) < 5
        ):  # first and last points are high temp
            trace_list.append(i)

    """ Plot Sweeps """
    for i in trace_list:
        time = np.asarray(
            x[time_diff_index[i] + 1 : time_diff_index[i + 1]], dtype=np.datetime64
        )
        temp = np.asarray(
            y[time_diff_index[i] + 1 : time_diff_index[i + 1]], dtype=np.float64
        )
        time_str = str(time[0])[0:10]
        network_path = r"S:\SC\InstrumentLogging\Cryogenics\Ice"
        file_name = os.path.join(network_path, time_str)
        data_dict = {"time": time, "temp": temp}
        scipy.io.savemat(file_name + "_cooldown.mat", mdict=data_dict)
        print("Saving %s" % (time_str))
        plt.plot(time, temp)
        plt.pause(2)
        plt.close()


# get_start_end(x,   y)

# %%
x, y = date_plot(path, "2021-03-30", "2021-04-03", plot=True)
save_cycle(x, y)

# %%


""" Things to do 


then extract data parameters such as, cooldown/wawrmup time, min temp. etc




"""
