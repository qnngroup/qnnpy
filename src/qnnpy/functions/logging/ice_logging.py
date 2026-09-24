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


def is_today(file_date: str) -> bool:
    today = datetime.now().strftime("%Y_%m_%d")
    if file_date == today:
        return True
    else:
        return False


def import_tdms(file_path, needlevalve_last) -> DataFrame:
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
            return format_data(data_dict), data_dict["Needle Valve 1"][-1]

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


def files_in_directory(directory: str) -> list:
    file_types = ["tdms"]
    files = []
    for file in os.listdir(directory):
        if file.split(".")[-1] in file_types:
            files.append(file)
    return files


def import_most_recent_tdms(directory: str) -> dict:
    files = files_in_directory(directory)
    files.sort()
    most_recent_file = files[-1]
    file_path = os.path.join(directory, most_recent_file)
    return import_tdms(file_path)


def get_uploaded_files(filename: str) -> list:
    with open(filename, "r") as file:
        files = file.read().splitlines()
    return files


def update_uploaded_files(logfile: str, file: str):
    with open(logfile, "a") as log:
        log.write(file + "\n")
    return


def check_and_import_tdms(directory: str, logfile: str, table_name: str):
    uploaded_files = get_uploaded_files(logfile)
    files = files_in_directory(directory)
    files.sort()

    try:
        conn = qf.database_connection()
        conn.auto_reconnect = True
    except mariadb.Error as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

    for file in files:
        if file not in uploaded_files:
            print(f"Importing: {file}")
            file_path = os.path.join(directory, file)
            file_date = file[0:10]

            data_frame = import_tdms(file_path)
            write_table_to_database(data_frame, table_name, conn)

            update_uploaded_files(logfile, file)
            time.sleep(5)

    conn.close()
    return
