import os 
import time
from typing import List
import scipy.io
import csv
from functions import log_data_to_database

#######################################################################
#       Temporary Data Storage and Cache-ing
#######################################################################


class Data:
    """
    The data class is used to store and save any collected data
    If no default file save location is provided, one will automatically be generated

    NOTE that autosaving does not work with .mat files due to how the binary
    data in a .mat file is stored. the only way to append to a mat file is
    to read the whole file into a python dictionary, modify, then re-write
    the entire thing, which defeats the purpose of "autosaving" to minimize
    memory usage.

    Parameters
    ----------
    autosave : bool, optional
        When enabled, periodically empties out Data and auto-saves it to the file location provided. The default is False.
        Note: If using autosave, remember to still call save() at the end to store any data in the current save_increment that hasn't been transferred yet!
    save_increment : int, optional
        How often to autosave whenever store() is called. The default is every 128th time store() is called.
    path : str, optional
        file path to save to. automatically sets up folders if full path doesn't exist. The default is None.
    name : str, optional
        file name to save to. if a name is already provided in path, it is overridden by this. The default is None.
    file_type : str, optional
        file type to save to. The default is 'csv'.
    preserve_pos_order : bool, optional
        if store(v1=1,v2=2) then store(v2=3, v3=4) is called, by default v1
        and v4 will be compressed into the first line, while v2 will appear
        on lines 1 and 2. Enabling preserve_pos_order will create empty
        columns to fix this ordering. The default is False.
    connection : mariadb.connection, optional
        If you want to auto-log data to a database, then you can set a connection here.
        Just remember to run connection.close() after you're done!
    table_name : str, optional
        database table name
    logtime: bool, optional
        logs the time in the data dict along with other variables whenever store() is called
    Returns
    -------
    None.

    """

    # data: dict[str,list[object]]
    data: dict
    numcalls: int  # number of times store is called, reset to 0 when empty() is called

    # save_increment = how often to save csv when calling store, every time (1), every other time (2)
    def __init__(
        self,
        *,
        autosave: bool = False,
        save_increment: int = 128,
        path: str = None,
        name: str = None,
        file_type: str = "csv",
        preserve_pos_order: bool = False,
        table_name: str = None,
        connection=None,
        logtime=False,
    ):
        self.data = {}
        self.numcalls = 0
        self.preserve_pos = preserve_pos_order
        self.connection = None
        self.connectionattempts = 0
        if path is not None:
            if "." in path:
                temp = path.rsplit(os.sep, 1)
                path = temp[0]
                if name is None:
                    name = temp[1]
            if not os.path.exists(path):
                os.makedirs(path)
        if name is None:
            name: str = time.strftime(
                f"data_%Y-%m-%d_%H-%M-%S.{file_type}", time.gmtime()
            )
        elif "." not in name:
            name = f"{name}.{file_type}"
        if path is None:
            self.save_loc = name
        else:
            self.save_loc = f"{path}{os.sep}{name}"
        # print(self.save_loc)
        self.autosave = autosave
        if autosave:
            # self.close_csv()
            self.save_increment = save_increment
            self.save_increment_counter = 0
        if connection is not None:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_name = '{0}'
                """.format(table_name.replace("'", "''"))
            )
            if not cursor.fetchone()[0] == 1:
                print(f"Table {table_name} does not exist.")
                connection.close()
            else:
                self.connection = connection
                self.dbtable_name = table_name
        self.logtime = logtime

    def store(self, **kwargs):
        if self.logtime:
            kwargs["time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        for key in kwargs:
            if self.data.get(key) is not None:
                self.data[key].append(kwargs[key])
            else:
                if self.preserve_pos and self.numcalls > 0:
                    self.data[key] = [""] * self.numcalls
                    self.data[key].append(kwargs[key])
                else:
                    self.data[key] = [kwargs[key]]
                exec(f"self.{key}=self.data['{key}']")
        if self.connection is not None:
            try:
                log_data_to_database(self.dbtable_name, self.connection, **kwargs)
                self.connectionattempts = 0
            except Exception as e:
                self.connectionattempts += 1
                print(f"Data failed to log to database: {e}")
                if (
                    self.connectionattempts > 10
                ):  # times out connection after 10 failed attempts
                    print(
                        "\033[1;31;49mDatabase connection has timed out, closing connection...\033[1;37;49m"
                    )
                    try:
                        self.connection.close()
                    except Exception:
                        pass
                    self.connection = None
        if self.preserve_pos and len(kwargs) < len(self.data):
            for key in self.data:
                if kwargs.get(key) is None:
                    self.data[key].append("")
        if self.autosave:
            self.save_increment_counter += 1
            if self.save_increment_counter >= self.save_increment:
                self.save(path=self.save_loc)
                if self.connection is not None:
                    try:
                        self.connection.commit()
                        self.connectionattempts = 0
                    except Exception as e:
                        self.connectionattempts += 1
                        print(f"Data failed to commit to database: {e}")
                        if (
                            self.connectionattempts > 10
                        ):  # times out connection after 10 failed attempts
                            print(
                                "\033[1;31;49mDatabase connection has timed out, closing connection...\033[1;37;49m"
                            )
                            try:
                                self.connection.close()
                            except Exception:
                                pass
                            self.connection = None
                self.empty()
                self.save_increment_counter = 0
        self.numcalls += 1

    def get(self, key: str) -> List[object]:
        return self.data[key]

    def last(self, key: str) -> object:
        return self.get(key)[-1]

    def empty(self):
        """
        empties out the values stored in the data dict, but retains any
        dictionary keys

        Returns
        -------
        None.

        """
        for key in self.data:
            self.data.get(key).clear()
        self.numcalls = 0

    def save(
        self,
        path: str = None,
        name: str = None,
        file_type: str = "csv",
        override: bool = False,
        printloc: bool = False,
    ):
        """
        saves the current contents of the data class to a file.
        if a default save location is provided in initialization, arguments
        provided here will override defaults, UNLESS no arguments are provided,
        (excluding override argument), in which case defaults will still be used

        note that if autosaving is enabled, then the data will periodically
        get cleared to save memory, which means not all data collected will be
        included in newer files created by save(), only the autosave file will
        include all data.

        also note: saving once to a .mat file works just fine, but attempting to
        append to a .mat file DOES NOT WORK. This also means that autosave does
        not work with .mat files.

        Parameters
        ----------
        path : str, optional
            file path to use. automatically sets up folders if full path doesn't exist. The default is None.
        name : str, optional
            file name to use. if a name is already provided in path, it is overridden by this. The default is None.
        file_type : str, optional
            file type. The default is 'csv'.
        override : bool, optional
            if to override previous file if it already exists. The default is False.
        Returns
        -------
        None
        """
        if path is None and name is None and file_type == "csv":
            path = self.save_loc
        if path is not None and os.sep not in path:
            name = path
            path = None
        if path is not None:
            if "." in path:
                temp = path.rsplit(os.sep, 1)
                path = temp[0]
                if name is None:
                    name = temp[1]
            if not os.path.exists(path):
                os.makedirs(path)
            # sys.path.append(path)
        if name is None:
            name: str = time.strftime(
                f"data_%Y-%m-%d_%H-%M-%S.{file_type}", time.gmtime()
            )
        elif "." not in name:
            name = f"{name}.{file_type}"
        if path is None:
            path = ""
        try:
            mode: str = "w"
            if os.path.exists(f"{path}{os.sep}{name}") and not override:
                mode = "a"
            if mode == "a" and name.rsplit(".", 1)[1] == "mat":
                mode = "ab"
            # print(mode + " " + str(os.path.exists(f"{path}{os.sep}{name}")) + " " + f"{path}{os.sep}{name}")
            with open(f"{path}{os.sep}{name}", mode) as f:
                if name.rsplit(".", 1)[1] == "mat":
                    # print(self.data)
                    if mode == "ab":
                        scipy.io.savemat(f, mdict=self.data)
                    else:
                        scipy.io.savemat(f"{path}{os.sep}{name}", mdict=self.data)
                    return
                writer = csv.writer(f)
                if mode == "w":
                    writer.writerow(self.data.keys())
                writer.writerows(zip(*self.data.values()))
            if printloc:
                print(f"{path}{os.sep}{name}")
        except IOError as e:
            # even if initial save attempt fails, will try to force store data in a temporary file at the script location
            print(
                f"\033[1;31;49mI/O error: {e}, attempting to force data save... \033[1;37;49m"
            )
            try:
                with open("forced_data_save.csv", "a") as f:
                    writer = csv.writer(f)
                    writer.writerow(self.data.keys())
                    writer.writerows(zip(*self.data.values()))
                print("data saved at *this user*\\forced_data_save.csv")
            except Exception as e:
                print(
                    f"Backup failed somehow, if you're seeing this things are really messed up: {e}"
                )
