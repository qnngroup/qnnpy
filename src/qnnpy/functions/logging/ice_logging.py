import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import mariadb
import nptdms
import numpy as np
import pandas as pd
from mariadb import Connection
from pandas.core.frame import DataFrame

import qnnpy.functions.functions as qf


def load_data_to_database(filename: str, table_name: str, connection: Connection):
    conn = connection
    file_path = os.path.join(filename)
    file_path = file_path.replace("\\", "/")
    cur = conn.cursor()
    command = f"LOAD DATA LOCAL INFILE '{file_path}' IGNORE INTO TABLE `{table_name}` FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\n';"

    try:
        cur.execute(command)
    except mariadb.IntegrityError:
        pass
    conn.commit()


def import_tdms(file_path, needlevalve_last, decimate=True) -> DataFrame:
    try:
        with nptdms.TdmsFile.open(file_path) as tdms_file:
            group = tdms_file["Data"]
            data_dict = {}

            for channel_name in group.channels():
                if channel_name.name in [
                    "Unix Timestamp",
                    "1k",
                    "4k",
                    "50k",
                    "SORB",
                    "Needle Valve 1",
                    "Dump Pressure",
                    "Circulation Pressure",
                ]:
                    channel = group[channel_name.name]
                    data_dict[channel_name.name] = channel[:]
            if needlevalve_last is None:
                needlevalve_last = data_dict["Needle Valve 1"][0]
            data_dict["diff_needlevalve"] = np.diff(
                np.concatenate(([needlevalve_last], data_dict["Needle Valve 1"]))
            )
            needlevalve_last = data_dict["Needle Valve 1"][-1]
            data_dict = format_data(data_dict)
            if decimate:
                data_dict_reduced = {}
                # last
                for name in ["epochtime", "datetime"]:
                    data_dict_reduced[name] = data_dict[name].tail(1)
                # mean
                for name in ["T1", "T2", "T3", "T4", "needlevalve", "pressure", "dump_pressure"]:
                    data_dict_reduced[name] = data_dict[name].mean(axis=0)
                # mean(abs)
                for name in ["diff_needlevalve"]:
                    data_dict_reduced[name] = data_dict[name].abs().mean(axis=0)
                data_dict = pd.DataFrame(data_dict_reduced)
            return data_dict, needlevalve_last

    except FileNotFoundError:
        print("Error: File not found!")


def format_data(data_dict: dict) -> DataFrame:
    df = pd.DataFrame(data_dict)
    df["date_time"] = pd.to_datetime(df["Unix Timestamp"], unit="s")
    df["date_time"] = df["date_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.iloc[:, [0, 9, 1, 2, 3, 4, 5, 7, 6, 8]]
    df.columns = [
        "epochtime",
        "datetime",
        "T1",
        "T2",
        "T3",
        "T4",
        "needlevalve",
        "pressure",
        "dump_pressure",
        "diff_needlevalve",
    ]
    return df


def export_to_csv(data_frame: DataFrame):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
        data_frame.to_csv(temp.name + ".log", index=False, header=False)
        return temp.name + ".log"


def write_table_to_database(data_frame: DataFrame, table_name: str, connection=None):
    temp_file = export_to_csv(data_frame)
    load_data_to_database(temp_file, table_name, connection)
    Path(temp_file).unlink()
    os.remove(temp_file[:-4])
    return

