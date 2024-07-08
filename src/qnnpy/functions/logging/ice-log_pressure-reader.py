import csv
import sys

# import schedule
import time
from datetime import datetime
from pathlib import Path

import mariadb
from numpy import array

sys.path.append(r"Q:\qnnpy")
import qnnpy.functions.functions as qf

PATH = "S:/SC/InstrumentLogging/Cryogenics/Ice/ice-log/Results/"


def load_data_to_database(filename: str, table_name: str, connection=None):
    if connection is not None:
        conn = connection
    else:
        conn = qf.database_connection()

    cur = conn.cursor()
    command = (
        "LOAD DATA LOCAL INFILE '%s' IGNORE INTO TABLE `%s` FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' "
        % (filename, table_name)
    )
    cur.execute(command)
    conn.commit()
    time.sleep(2)
    conn.close()


def log_many_rows_to_database(table_name: str, connection=None, **kwargs):
    """
    table_name [str]: name of table to insert rows to
    kwargs: should be of form COLUMN_NAME:[list, of, values, in, column]

    executemany takes two arguments:
        -1) the command string, with VALUES (%s, %s...%s) for #columns to write
        -2) a list of tuples of rows, e.g.
            data = [
                (row1_column1, row1_column2, ...row1_columnn),
                ...
                (rowm_column1, rowm_column2, ...rowm_columnn)
            ]
    """
    if connection is not None:
        conn = connection
    else:
        conn = qf.database_connection()

    cur = conn.cursor()
    column_names = "`" + "`, `".join(kwargs.keys()) + "`"
    values_sideways = array([v for v in kwargs.values()])
    values = values_sideways.T.tolist()
    # values = "'"+"', '".join([str(v) for v in kwargs.values()])+"'"
    for value in values:
        try:
            command = "INSERT INTO `%s` (%s) VALUES (%s)" % (
                table_name,
                column_names,
                str(value)[1:-1],
            )
            cur.execute(command)
            conn.commit()
            time.sleep(0.5)
        except mariadb.IntegrityError:
            pass
    if connection is None:
        conn.close()


def read_ice_log(path, date=False):
    log_columns = {
        "date": [],
        "time": [],
        "epochtime": [],
        "date_time": [],
        "T1": [],
        "T2": [],
        "T3": [],
        "T4": [],
        "sensor1": [],
        "sensor2": [],
        "sensor3": [],
        "sensor4": [],
        "heater1": [],
        "heater2": [],
        "needlevalve": [],
        "needlevalve2": [],
        "null1": [],
        "null2": [],
        "setpoint2": [],
        "20_1": [],
        "ramprate2": [],
        "null3": [],
        "P": [],
        "I": [],
        "D": [],
        "50_1": [],
        "20_2": [],
        "null4": [],
        "null5": [],
        "dump_pressure": [],
    }

    datetime_format = "%m/%d/%Y %I:%M:%S %p"

    if not date:
        # yesterday = datetime.now() - timedelta(1)
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")

    path = path + date + "/"

    try:
        with open(path + date + ".log") as csvfile:
            read = csv.reader(csvfile)

            with open(path + "temp.log", "w", newline="\n") as csvfile:
                write = csv.writer(csvfile, delimiter=",")

                for i, row in enumerate(read):
                    log_columns["epochtime"].append(int(row[2]))
                    datetime_data = datetime.strftime(
                        datetime.strptime(row[3], datetime_format), "%Y-%m-%d %H:%M:%S"
                    )
                    log_columns["date_time"].append(datetime_data)
                    log_columns["T1"].append(float(row[4]))
                    log_columns["T2"].append(float(row[5]))
                    log_columns["T3"].append(float(row[6]))
                    log_columns["T4"].append(float(row[7]))
                    log_columns["needlevalve"].append(float(row[14]))
                    log_columns["dump_pressure"].append(float(row[29]))

                    write.writerow(
                        [
                            log_columns["epochtime"][i],
                            log_columns["date_time"][i],
                            log_columns["T1"][i],
                            log_columns["T2"][i],
                            log_columns["T3"][i],
                            log_columns["T4"][i],
                            log_columns["needlevalve"][i],
                            log_columns["dump_pressure"][i],
                        ]
                    )
    except Exception as e:
        print(e)
        time.sleep(600)

    load_data_to_database(path + "temp.log", "ice_log")
    file_to_rem = Path(path + "temp.log")
    file_to_rem.unlink()
    return


# schedule.every().day.at('01:00').do(read_ice_log, path=PATH)
# schedule.every(10).minutes.do(read_ice_log, path=PATH)

while True:
    read_ice_log(PATH)
    time.sleep(120)
