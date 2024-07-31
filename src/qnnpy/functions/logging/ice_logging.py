import os
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

import mariadb
import nptdms
import pandas as pd
from mariadb import Connection
from pandas.core.frame import DataFrame

import qnnpy.functions.functions as qf


def load_data_to_database(filename: str, table_name: str, connection: Connection):
    conn = connection
    file_path = os.path.join(filename)
    file_path = file_path.replace("\\", "/")
    print(f"Loading tempfile: {file_path}")
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


def import_tdms(file_path) -> DataFrame:
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

            return format_data(data_dict)

    except FileNotFoundError:
        print("Error: File not found!")


def format_data(data_dict: dict) -> DataFrame:
    df = pd.DataFrame(data_dict)
    df["date_time"] = pd.to_datetime(df["Unix Timestamp"], unit="s")
    df["date_time"] = df["date_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df = df.iloc[:, [0, 8, 1, 2, 3, 4, 5, 7, 6]]
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


if __name__ == "__main__":
    LOG_DIRECTORY = r"S:\SC\InstrumentLogging\Cryogenics\Ice\ice-log\Logs"
    LOG_FILE = r"S:\SC\InstrumentLogging\Cryogenics\Ice\ice-log\uploaded_files.txt"
    TABLE_NAME = "ice_log"

    check_and_import_tdms(LOG_DIRECTORY, LOG_FILE, TABLE_NAME)


# --------------------------------------------------------------------------------------------
# Archived functions for ICE Software V2.0
# --------------------------------------------------------------------------------------------

# def log_many_rows_to_database(table_name: str, connection=None, **kwargs):
#     """
#     table_name [str]: name of table to insert rows to
#     kwargs: should be of form COLUMN_NAME:[list, of, values, in, column]

#     executemany takes two arguments:
#         -1) the command string, with VALUES (%s, %s...%s) for #columns to write
#         -2) a list of tuples of rows, e.g.
#             data = [
#                 (row1_column1, row1_column2, ...row1_columnn),
#                 ...
#                 (rowm_column1, rowm_column2, ...rowm_columnn)
#             ]
#     """
#     if connection is not None:
#         conn = connection
#     else:
#         conn = qf.database_connection()

#     cur = conn.cursor()
#     column_names = "`" + "`, `".join(kwargs.keys()) + "`"
#     values_sideways = array([v for v in kwargs.values()])
#     values = values_sideways.T.tolist()
#     # values = "'"+"', '".join([str(v) for v in kwargs.values()])+"'"
#     for value in values:
#         try:
#             command = "INSERT INTO `%s` (%s) VALUES (%s)" % (
#                 table_name,
#                 column_names,
#                 str(value)[1:-1],
#             )
#             cur.execute(command)
#             conn.commit()
#             time.sleep(0.5)
#         except mariadb.IntegrityError:
#             pass
#     if connection == None:
#         conn.close()


# def read_ice_log(path, date=False):
#     log_columns = {
#         "date": [],
#         "time": [],
#         "epochtime": [],
#         "date_time": [],
#         "T1": [],
#         "T2": [],
#         "T3": [],
#         "T4": [],
#         "sensor1": [],
#         "sensor2": [],
#         "sensor3": [],
#         "sensor4": [],
#         "heater1": [],
#         "heater2": [],
#         "needlevalve": [],
#         "needlevalve2": [],
#         "null1": [],
#         "null2": [],
#         "setpoint2": [],
#         "20_1": [],
#         "ramprate2": [],
#         "null3": [],
#         "P": [],
#         "I": [],
#         "D": [],
#         "50_1": [],
#         "20_2": [],
#         "null4": [],
#         "null5": [],
#         "dump_pressure": [],
#     }

#     datetime_format = "%m/%d/%Y %I:%M:%S %p"

#     if not date:
#         # yesterday = datetime.now() - timedelta(1)
#         date = datetime.strftime(datetime.now(), "%Y-%m-%d")

#     path = path + date + "/"

#     try:
#         with open(path + date + ".log") as csvfile:
#             read = csv.reader(csvfile)

#             with open(path + "temp.log", "w", newline="\n") as csvfile:
#                 write = csv.writer(csvfile, delimiter=",")

#                 for i, row in enumerate(read):
#                     log_columns["epochtime"].append(int(row[2]))
#                     datetime_data = datetime.strftime(
#                         datetime.strptime(row[3], datetime_format), "%Y-%m-%d %H:%M:%S"
#                     )
#                     log_columns["date_time"].append(datetime_data)
#                     log_columns["T1"].append(float(row[4]))
#                     log_columns["T2"].append(float(row[5]))
#                     log_columns["T3"].append(float(row[6]))
#                     log_columns["T4"].append(float(row[7]))
#                     log_columns["needlevalve"].append(float(row[14]))
#                     log_columns["dump_pressure"].append(float(row[29]))

#                     write.writerow(
#                         [
#                             log_columns["epochtime"][i],
#                             log_columns["date_time"][i],
#                             log_columns["T1"][i],
#                             log_columns["T2"][i],
#                             log_columns["T3"][i],
#                             log_columns["T4"][i],
#                             log_columns["needlevalve"][i],
#                             log_columns["dump_pressure"][i],
#                         ]
#                     )
#     except Exception as e:
#         print(e)
#         time.sleep(600)

#     load_data_to_database(path + "temp.log", "ice_log")
#     file_to_rem = Path(path + "temp.log")
#     file_to_rem.unlink()
#     return
