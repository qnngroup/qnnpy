# -*- coding: utf-8 -*-
"""
Created on Thu May  7 10:16:58 2020

@author: omedeiro
"""

import csv
import datetime as dt
import logging
import os
import re
import sys
import time
from datetime import datetime
from enum import Enum
from time import sleep
from typing import List

import mariadb
import numpy as np
import scipy.io
import yaml
from mariadb import Connection
from matplotlib import pyplot as plt

if sys.platform == "win32":
    import win32com.client

###############################################################################
# Plotting
###############################################################################


class LogLevel(Enum):
    all_logs = 0
    debugging = 1
    warn = 2
    error = 3
    silent = 4


def plot(
    xdata,
    ydata,
    x_scale="linear",
    y_scale="linear",
    title="",
    xlabel="",
    ylabel="",
    label="",
    linestyle="o",
    path="",
    close=True,
    show=True,
):
    """
    update to using **kwargs https://book.pythontips.com/en/latest/args_and_kwargs.html

    accepts arrays or lists of arrays. Scale is the same as plt.xscale().
    If path is specified the figure will be saved to that location.
    Close and Show are true by default.

    """

    if close:
        plt.close()

    if isinstance(ydata, list) and not isinstance(xdata, list):
        if label:
            for i in np.arange(0, len(ydata), 1):
                plt.plot(xdata, ydata[i], linestyle, label=label[i])
        else:
            for i in np.arange(0, len(ydata), 1):
                plt.plot(xdata, ydata[i], linestyle)

    elif isinstance(ydata, list) and isinstance(xdata, list):
        if label:
            for i in np.arange(0, len(ydata), 1):
                plt.plot(xdata[i], ydata[i], linestyle, label=label[i])
        else:
            for i in np.arange(0, len(ydata), 1):
                plt.plot(xdata[i], ydata[i], linestyle)
    else:
        plt.plot(xdata, ydata, linestyle)

    plt.xscale(x_scale)
    plt.yscale(y_scale)

    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)
    if title:
        plt.title(title)
    if label:
        plt.legend()
    if not path == "":
        if isinstance(path, tuple):
            path = path[0]
        plt.savefig(path + ".png", bbox_inches="tight")
        print("File Saved:\n %s" % path)
    if show:  # show should always be after save
        plt.show()
    return plt


def plot_new(x, y, **kwargs):
    plt.plot(x, y)
    for key, value in kwargs.items():
        plt.__dict__[key](value)

    return plt


# Requires IPython for interactive shell
class LivePlotter:
    """
    Automatically updating plotter
    Requires IPython to be enabled for interactive shell
    Simpily call plot(x, y) and the plot will add your points live
    Once you're done, you can save by calling save()
    """

    # data: dict[str, (list[float],list[float],list[float])]
    data: dict

    # __subplots: dict[str, plt.Subplot]
    def __init__(
        self,
        *,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        legend: bool = False,
        legend_loc: str = "best",
        max_len: int = -1,
    ):
        self.data = {}
        if not plt.isinteractive():
            plt.ion()
        self.fig, self.ax = plt.subplots()
        # self.__subplots = {}
        # self.start_time: float = 0
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        self.show_legend: bool = legend
        self.legend_loc: str = legend_loc
        self.max_len = max_len
        self.def_col_idx = 0
        self.colors = ["r", "g", "b", "c", "m", "y", "k"]
        # plt.xlim(0,1)
        # plt.ylim(0,1)
        plt.draw()

    def plot(
        self,
        x: float,
        y: float,
        label: str = "",
        *,
        linestyle="solid",
        color=None,
        marker="o",
        linewidth=3,
        markercolor=None,
    ):
        # if self.start_time == 0:
        # self.start_time = time.time()
        if markercolor is None:
            markercolor = color
        if self.data.get(label) is None:
            self.data[label] = ([x], [y], self.colors[self.def_col_idx])
            self.def_col_idx += 1
            # self.data[label]=([x],[y],[time.time()-self.start_time])
        else:
            self.data[label][0].append(x)
            self.data[label][1].append(y)
            if color is None:
                color = self.data[label][2]
            if self.max_len > 1 and len(self.data[label][0]) > self.max_len:
                self.data[label][0].pop(0)
                self.data[label][1].pop(0)
            # self.data[label][2].append(time.time()-self.start_time)
        if len(self.ax.lines) >= len(self.data):
            self.ax.lines.pop(0)  # beware memory leaks and other shenanagins
        self.ax.plot(
            self.data[label][0],
            self.data[label][1],
            label=label,
            linestyle=linestyle,
            color=color,
            marker=marker,
            linewidth=linewidth,
            markerfacecolor=markercolor,
            markeredgecolor=markercolor,
        )
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        if self.show_legend:
            self.ax.legend(loc=self.legend_loc)

    def save(self, path: str = None, name: str = None, file_type: str = "jpg"):
        if path is not None:
            if "." in path:
                temp = path.rsplit(os.sep, 1)
                path = temp[0]
                if name is None:
                    name = temp[1]
            if not os.path.exists(path):
                os.makedirs(path)
            sys.path.append(path)
        if name is None:
            name: str = time.strftime(
                f"plot_%Y-%m-%d_%H-%M-%S.{file_type}", time.gmtime()
            )
        elif "." not in name:
            name = f"{name}.{file_type}"
        self.fig.savefig(f"{path}{os.sep}{name}")


###############################################################################
# Configuration
###############################################################################


def load_config(filename=None):
    """Load config accepts the full name of a .yaml file. The sample name is
    check for correct format (XXX123).
    If verified, the file is loaded and the parameters are returned.
    """
    # Check if there is a file
    parameters = {}
    if filename is None:
        raise ValueError("Please enter filename")

    # Open file
    with open(filename) as f:
        parameters = yaml.load(f, Loader=yaml.FullLoader)

    if parameters.get("Save File"):
        if parameters.get("Save File").get("sample name"):
            sample_name = parameters["Save File"]["sample name"]
            check_sample_name(sample_name)
        elif parameters.get("Save File").get("sample name 1"):
            for i in range(5):
                if parameters["Save File"].get(f"sample name {i+1}") is None:
                    break
                check_sample_name(parameters["Save File"][f"sample name {i+1}"])

    # No longer accepting path location. FIXED PATH TO NETWORK
    #    file_path=parameters['Save File']['filepath']
    #    check_file_path(file_path)

    return parameters


def check_sample_name(sample_name):
    """The sample name is required to match the XXX123 format."""
    result = re.match("^[A-Z]{3}[0-9]{3}$", sample_name)
    if not result:
        lablog_error('Invalid Sample Name. Name entered: "%s"' % sample_name)
        raise NameError("Invalid Sample Name. String must match XXX###")


def check_file_path(file_path):
    if not os.path.exists(file_path):
        try:
            os.makedirs(file_path)
        except Exception:
            lablog_error('Invalid Path. Path entered: "%s"' % file_path)
            raise NameError("Invalid Path")


###############################################################################
# Saving
###############################################################################


def save(
    parameters, measurement, data_dict={}, instrument_list=None, db=False, meas_txt=None
):
    """Save follows the typical format of defining a data dictionary (data_dict) and saving as a .mat .
    This function requires parameters from a loaded config file. The file is saved on the S:\ drive according to the configuration settings.
    If the data_dict is not included this function returns the path created from the configuration file.

    """
    if not isinstance(parameters, dict):
        raise ValueError("save accepts dict from configured .yml file")

    if "Save Root" in parameters:
        file_path = parameters["Save Root"]
    else:
        file_path = "S:\SC\Measurements"
    # Setup variables from parameters for file path
    user = parameters["User"]["name"]
    sample_name = parameters["Save File"][
        "sample name"
    ]  # this field should describe the material SPX111 or GaN_ID#20
    device_name = parameters["Save File"][
        "device name"
    ]  # this field should describe which device is being tested
    device_type = parameters["Save File"][
        "device type"
    ]  # this field should describe device type ntron, snspd, coupler, memory

    if parameters["Save File"].get("port"):
        device_type_ext = device_type + "_" + parameters["Save File"]["port"]
        port = parameters["Save File"]["port"]
    else:
        device_type_ext = device_type
        port = 1

    if parameters["Save File"].get("cell"):
        cell_name = parameters["Save File"]["cell"] + "_"
    else:
        cell_name = None

    time_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    """ Shorten parameter list to only include current measurement and the instruments used"""
    if instrument_list:
        new_parameters = {}
        new_parameters["User"] = parameters["User"]
        new_parameters["Save File"] = parameters["Save File"]
        new_parameters[measurement] = parameters[measurement]
        for i in range(len(instrument_list)):
            new_parameters[instrument_list[i]] = parameters[instrument_list[i]]
        parameters = new_parameters

    """ Create folder and save .mat file. """
    while os.path.exists(file_path):
        if meas_txt:
            measurement_alt = measurement + meas_txt
        else:
            measurement_alt = measurement

        file_name = (
            sample_name
            + "_"
            + measurement_alt
            + "_"
            + device_type_ext
            + "_"
            + device_name
            + "_"
            + cell_name
            + time_str
        )
        if parameters["Save File"].get("cell"):
            file_path = os.path.join(
                file_path,
                sample_name,
                device_type,
                device_name,
                measurement,
                parameters["Save File"]["cell"],
            )
        else:
            file_path = os.path.join(
                file_path, sample_name, device_type, device_name, measurement
            )
        os.makedirs(file_path, exist_ok=True)
        full_path = os.path.join(file_path, file_name)
        if data_dict:
            scipy.io.savemat(full_path + ".mat", mdict=data_dict)
            output_log(parameters, full_path)
            print("File Saved:\n %s" % full_path)
            try:
                insert_measurement_event(
                    user, measurement, sample_name, device_type, device_name, port
                )
            except Exception as e:
                print(f"Logging to qnndb failed. ({e})")

        break

    return full_path, time_str


# same as save but uses data instruments and liveplotter class
def data_saver(
    parameters: dict,
    measurement: str,
    meas_path: str = r"S:\SC\Measurements",
    data=None,
    inst=None,
    plot=None,
    file_name_append: str = "",
):
    """

    Parameters
    ----------
    parameters : dict
        parameters from loaded yaml config file.
    measurement : str
        name of the measurement: ie, iv_sweep.
    meas_path : str, optional
        root folder location for measurements to be saved to. The default is r'S:\SC\Measurements'.
    data : Data or List[Data], optional
        data class to save. The default is None.
        if a list is provided, then iteratively saves each element seperately. If multiple samples are defined in parameters, each iterative save will use the next sample
    inst : Instruments, optional
        instruments that were used. The default is None.
    plot : LivePlotter or List[LivePlotter], optional
        optionally save the live plotter which was used. The default is None.
        if a list is provided, does the same thing as data if data is a list
    Raises
    ------
    ValueError
        if there is an error in parameters.

    Returns
    -------
    full_path : str or list[str]
        full path of where data was saved.
        if multiple samples are used, an array of paths for each sample save location is given back

    """
    # for saving multiple samples
    if (
        parameters.get("Save File")
        and parameters.get("Save File").get("sample name") is None
    ):
        res: list = []
        for i in range(4):  # maximum of 4 samples can be saved at a time
            if parameters["Save File"].get(f"sample name {i+1}") is None:
                break
            d = data[i % len(data)] if isinstance(data, list) else data
            p = plot[i % len(plot)] if isinstance(plot, list) else plot
            parameters["Save File"] = (
                {} if parameters.get("Save File") is None else parameters["Save File"]
            )
            parameters["Save File"]["sample name"] = (
                parameters["Save File"][f"sample name {i+1}"]
                if parameters["Save File"].get(f"sample name {i+1}")
                else (
                    parameters.get("Save File").get("sample name")
                    if parameters.get("Save File").get("sample name")
                    else ""
                )
            )
            res.append(
                data_saver(
                    parameters,
                    measurement,
                    meas_path,
                    data=d,
                    inst=inst,
                    plot=p,
                    file_name_append=str(i),
                )
            )
        return res
    # if type(data) == list or type(plot) == list:
    if isinstance(data, list) or isinstance(plot, list):
        res: list = []
        for i in range(max(len(data), len(plot))):
            d = data[i % len(data)] if isinstance(data, list) else data
            p = plot[i % len(plot)] if isinstance(plot, list) else plot
            res.append(
                data_saver(
                    parameters,
                    measurement,
                    meas_path,
                    data=d,
                    inst=inst,
                    plot=p,
                    file_name_append=str(i),
                )
            )
        return res

    # ensure parameters is dict
    # if type(parameters) != dict:
    if isinstance(parameters, dict) is False:
        try:
            parameters = load_config(parameters)
        except Exception as e:
            raise ValueError(
                "save accepts dict from configured .yml file, try using load_config(parameters) first!"
            )
    file_path = meas_path
    # Setup variables from parameters for file path
    user = (
        parameters["User"]["name"]
        if parameters.get("User") and parameters.get("User").get("name")
        else ""
    )
    if parameters.get("Save File"):
        sample_name = (
            parameters["Save File"]["sample name"]
            if parameters.get("Save File").get("sample name")
            else ""
        )  # this field should describe the material SPX111 or GaN_ID#20
        device_name = (
            parameters["Save File"]["device name"]
            if parameters.get("Save File").get("device name")
            else ""
        )  # this field should describe which device is being tested
        device_type = (
            parameters["Save File"]["device type"]
            if parameters.get("Save File").get("device type")
            else ""
        )  # this field should describe device type ntron, snspd, coupler, memory
    else:
        sample_name, device_name, device_type = "", "", ""
    if parameters["Save File"].get("port"):
        device_type_ext = device_type + "_" + f"port{parameters['Save File']['port']}"
        port = parameters["Save File"]["port"]
    else:
        device_type_ext = device_type
        port = 1
    # Shorten parameter list to only include current measurement and the instruments used
    if inst and len(inst.instrument_list) > 0:
        new_parameters = {
            "User": parameters.get("User"),
            "Save File": parameters.get("Save File"),
            "Measurement": parameters.get(measurement),
        }
        new_parameters = {key: parameters[key] for key in inst.instrument_list}
        # for i in range(len(inst.instrument_list)):
        #     new_parameters[inst.instrument_list[i]] = parameters[inst.instrument_list[i]]
        parameters = new_parameters
    # Create folder and save .mat file
    full_path = file_path
    if os.path.exists(file_path):
        # if meas_txt:
        #     measurement_alt = measurement+meas_txt
        # else:
        #     measurement_alt = measurement
        # makes file path
        time_str = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        file_name = (
            sample_name
            + "_"
            + measurement
            + "_"
            + device_type_ext
            + "_"
            + device_name
            + "_"
            + time_str
            + (f"_({file_name_append})" if file_name_append != "" else "")
        )
        file_path = os.path.join(
            file_path, sample_name, device_type, device_name, measurement
        )
        os.makedirs(file_path, exist_ok=True)
        full_path = os.path.join(file_path, file_name)
        if data:
            # scipy.io.savemat(full_path + '.mat', mdict=data.data)
            data.save(path=f"{full_path}.mat")
            output_log(parameters, full_path)
            print("File Saved:\n %s" % full_path)
            # make "recents" shortcut
            try:
                if sys.platform == "win32":
                    recents = os.path.join(meas_path, "recents")
                    os.makedirs(recents, exist_ok=True)
                    recents_path = os.path.join(
                        recents, f"{sample_name}_measurement_{time_str}.lnk"
                    )
                    target = file_path
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(recents_path)
                    shortcut.Targetpath = target
                    shortcut.save()
                else:
                    print("Only windows is supported for recent measurement shortcut")
            except Exception as e:
                print(f"failed to make shortcut in for recents: {e}")
            # saving to database
            try:
                log_data_to_database(
                    "measurement_events",
                    connection=None,
                    user=user,
                    meas_type=measurement,
                    sample_name=sample_name,
                    device_type=device_type,
                    device_id=device_name,
                    port=port,
                )
                # insert_measurement_event(user, measurement, sample_name, device_type, device_name, port)
            except Exception as e:
                print(f"Logging to qnndb failed: {e}")
        if plot:
            plot.save(path=f"{full_path}.png")
    else:
        print(
            "\033[1;31;49mmeas_path does not exist, forcing a save elsewhere: \033[1;37;49m"
        )
        data.save(printloc=True)
        plot.save(name="forced_plot_save")
    return full_path


###########################################################################
# Loggging
###########################################################################


def insert_measurement_event(
    user, meas_type, sample_name, device_type, device_id, port=1
):
    """ """
    conn = database_connection()
    # Get Cursor
    cur = conn.cursor()

    sql = (
        "INSERT INTO `measurement_events` (`user`, `meas_type`, `sample_name`, `device_type`, `device_id`, `port`) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"
        % (user, meas_type, sample_name, device_type, device_id, port)
    )
    cur.execute(sql)
    conn.commit()
    return cur


def lablog_error(message):
    """
    The lablog method logs errors to 'S:\SC\ErrorLogging'
    """
    # formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # log = logging.getLogger('lablog')
    # if not log.handlers:
    #     handler = logging.FileHandler('S:\SC\Logging\qnn-lablog.log')
    #     handler.setFormatter(formatter)

    #     log.setLevel(logging.ERROR)
    #     log.addHandler(handler)
    #     log.propagate = False

    # log.error(message)

    timestamp = str(datetime.now()) + " "
    path = r"S:\SC\ErrorLogging\lablog_error.txt"
    file = open(path, "a")

    file.write(timestamp + message + " \n")
    file.close()


def lablog_measurement(parameters, measurement=None):
    """
    The lablog_measurement method logs the measurement history within the lab.

    """
    if isinstance(parameters, dict) is False:
        raise ValueError("log_measurement accepts dictionary from configured .yml file")
    formatter = logging.Formatter(
        "%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
    )
    lab_measurement_log = logging.getLogger("lab_measurement_log")
    if not lab_measurement_log.handlers:
        handler = logging.FileHandler(
            "S:\SC\MeasurementLogging\qnn-lablog-measurement.log"
        )
        handler.setFormatter(formatter)

        lab_measurement_log.setLevel(logging.INFO)
        lab_measurement_log.addHandler(handler)
        lab_measurement_log.propagate = False

    if measurement:
        parameters["Save File"]["measurement"] = measurement
    lab_measurement_log.info(parameters)


def output_log(parameters, path):
    """
    The output_log method logs the configuration file used for each measurement
    to the file location where that measurement is saved.

    """
    # formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    # output_log = logging.getLogger('output_log')
    # formatter = logging.Formatter('%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    # handler = logging.FileHandler(path+'.txt')
    # handler.setFormatter(formatter)

    # output_log.setLevel(logging.INFO)
    # output_log.addHandler(handler)

    # output_log.info(parameters)

    file = open(path + ".txt", "w")
    file.write("\n".join("{}\t\t{}".format(k, v) for k, v in parameters.items()))
    file.close()


def database_connection(**kwargs) -> Connection:
    if kwargs is None or len(kwargs) == 0:
        try:
            with open(r"S:\SC\mariadb_conn.yml") as f:
                conn_params = yaml.load(f, Loader=yaml.FullLoader)
                conn = mariadb.connect(**conn_params)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            raise ConnectionError
    else:
        try:
            conn: Connection = mariadb.connect(kwargs)
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            raise ConnectionError
    return conn


def log_data_to_database(table_name: str, connection=None, **kwargs):
    if connection is None:
        connection = database_connection()
    cur = connection.cursor()
    column_names = "`" + "`, `".join(kwargs.keys()) + "`"
    values = "'" + "', '".join([str(v) for v in kwargs.values()]) + "'"
    command = "INSERT INTO `%s` (%s) VALUES (%s)" % (table_name, column_names, values)
    cur.execute(command)
    connection.commit()
    connection.close()


def update_table(
    table_name: str, set_col: str, conditional: str = "NULL", connection=None
):
    """

    Parameters
    ----------
    table_name : str
        name of table to update.
    set_col : str
        SET sql command, for example set_col = 'thickness=0, tc=0'.
    conditional : str
        WHERE sql command, arguments without '=' will simpily get matched using '=' operator to columns in set_col.
        to update an entire column without conditional, 'ALL'
    connection : TYPE, optional
        connection to database. The default is qnndb database.
    Returns
    -------
    None.

    """
    if connection is None:
        connection = database_connection()
    command: str = "UPDATE %s SET %s" % (table_name, insert_quotes(set_col))
    if not conditional == "ALL":
        conditional = insert_quotes(conditional)
        command += " WHERE "
        conditional_operators: list[str] = [
            "=",
            ">",
            "<",
            ">=",
            "<=",
            "!=",
            "BETWEEN",
            "LIKE",
            "IN",
        ]
        if any(op in conditional for op in conditional_operators):
            command += conditional
        else:
            cols: list[str] = get_column_names(set_col)
            vals: list[str] = conditional.split(",")
            for c, v in zip(cols, vals):
                command += f"{c}={v.strip()}, "
            command = command.rstrip(", ")
    cur = connection.cursor()
    print(command)
    cur.execute(command)
    connection.commit()
    connection.close()


def get_column_names(string: str):
    """
    Helper method for update_table to get the column names when an input is formatted as 'col=val, col2=val2, col3=val3' etc
    Parameters
    ----------
    string : str
        sql command formatted as 'column=value, column=value...'

    Returns
    -------
    list of column names
    """
    res = []
    builder = ""
    build = True
    for c in string:
        if c == "=":
            res.append(builder)
            builder = ""
            build = False
        elif build:
            if not c.isspace():
                builder += c
        elif c == ",":
            build = True
    return res


def insert_quotes(string: str) -> str:
    res: str = ""
    i: int = 0
    while i < len(string):
        c = string[i]
        res += c
        if c == "=":
            is_string = False
            builder = ""
            end: int = i
            for j in range(i + 1, len(string)):
                end = j
                if string[j] == "," or (is_string and string[j] == " "):
                    end = j - 1
                    break
                if not (
                    string[j].isnumeric()
                    or string[j] == "."
                    or string[j] == "-"
                    or string[j].isspace()
                ):
                    is_string = True
                builder += string[j]
            builder = builder.strip()
            if not is_string or builder.upper() == "NULL":
                res += builder
            else:
                res += f"'{builder}'"
            i = end
        i += 1
    return res


###########################################################################
# Measurement
###########################################################################


def ice_get_temp(select=None):
    """Access ICE log to return lakeshore 336 temperature.

    If the optional input 'select' is specified (as an int between 0-4)
    the dictionary index is returned. Else all of the
    values are returned as a dictionary.

    data_dict = {'date1':date1,
                   'temp1':temp1,
                   'temp2':temp2,
                   'temp3':temp3,
                   'temp4':temp4}

    """
    now = datetime.now()
    while not os.path.exists(
        r"S:\SC\InstrumentLogging\Cryogenics\Ice\ice-log\Results\%s" % str(now)[:10]
    ):
        sleep(1)

    f = (
        r"S:\SC\InstrumentLogging\Cryogenics\Ice\ice-log\Results\%s\%s"
        % (str(now)[:10], str(now)[:10])
        + ".log"
    )

    with open(f) as f:  # Get txt from log file and split the last (most recent) entry
        last = f.readlines()[-1].split(",")

        then = datetime.strptime(last[0] + " " + last[1], "%m/%d/%Y %I:%M:%S %p")

        if now - then > dt.timedelta(minutes=1):
            temp1 = ""
            print("TEMPERATURE: ICE Logging is off")
        else:
            date1 = last[3]
            temp1 = float(last[4])  # A
            temp2 = float(last[5])
            temp3 = float(last[6])
            temp4 = float(last[7])

    data_dict = {
        "date1": date1,
        "temp1": temp1,
        "temp2": temp2,
        "temp3": temp3,
        "temp4": temp4,
    }
    data_list = [date1, temp1, temp2, temp3, temp4]
    if select:
        select_temp = data_list[select]
        return select_temp
    else:
        return data_dict


#######################################################################
#       Code testing
#######################################################################


def mock_builder(class_to_mock) -> object:
    """
    Cool class mocking method
    Takes in a class (ie: mock_builder(float)), returns a new instance
    of that class (ie: Mockfloat), with mock versions of the original's
    methods that print out when the method is called

    Parameters
    ----------
    class_to_mock : CLASS
        Class that you want to make a mock version of, such as for testing

    Returns
    -------
    Object
        Mock instance of the inputted class.

    """
    method_list: List[str] = [
        func for func in dir(class_to_mock) if callable(getattr(class_to_mock, func))
    ]
    gen_code: str = f"class Mock{class_to_mock.__name__}:"
    for m in method_list:
        if not (m.startswith("__") and not m == "__init__"):
            gen_code += f"\n\tdef {m}(*placeholder):\n\t\tprint('\033[1;33;49mMocking: \033[1;36;49mcalled \033[1;35;49m{m}()\033[1;36;49m in \033[0;35;49mMock{class_to_mock.__name__}\033[1;37;49m')\n\t\treturn None"
    exec(gen_code)
    return eval(f"Mock{class_to_mock.__name__}")