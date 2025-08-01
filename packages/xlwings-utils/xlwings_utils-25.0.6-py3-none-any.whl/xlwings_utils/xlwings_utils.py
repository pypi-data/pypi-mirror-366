#         _            _                                   _    _  _
#  __  __| |__      __(_) _ __    __ _  ___         _   _ | |_ (_)| | ___
#  \ \/ /| |\ \ /\ / /| || '_ \  / _` |/ __|       | | | || __|| || |/ __|
#   >  < | | \ V  V / | || | | || (_| |\__ \       | |_| || |_ | || |\__ \
#  /_/\_\|_|  \_/\_/  |_||_| |_| \__, ||___/ _____  \__,_| \__||_||_||___/
#                                |___/      |_____|

__version__ = "25.0.6"


import dropbox
from pathlib import Path
import os
import sys
import math
import base64

dbx = None
Pythonista = sys.platform == "ios"
try:
    import xlwings

    xlwings = True
except ImportError:
    xlwings = False

missing = object()


def dropbox_init(refresh_token=missing, app_key=missing, app_secret=missing, **kwargs):
    """
    dropbox initialize

    This function may to be called prior to using any dropbox function
    to specify the request token, app key and app secret.
    If these are specified as REFRESH_TOKEN, APP_KEY and APP_SECRET
    environment variables, it is no necessary to call dropbox_init().

    Parameters
    ----------
    refresh_token : str
        oauth2 refreshntoken

        if omitted: use the environment variable REFRESH_TOKEN

    app_key : str
        app key

        if omitted: use the environment variable APP_KEY


    app_secret : str
        app secret

        if omitted: use the environment variable APP_SECRET

    Returns
    -------
    -
    """
    global dbx

    if Pythonista:
        # under Pythonista, the environ is updated from the .environ.toml file, if present
        environ_file = Path(os.environ["HOME"]) / "Documents" / ".environ.toml"

        if environ_file.is_file():
            with open(environ_file, "r") as f:
                import toml

                d = toml.load(f)
                os.environ.update(d)

    if refresh_token is missing:
        if "REFRESH_TOKEN" in os.environ:
            refresh_token = os.environ["REFRESH_TOKEN"]
        else:
            raise ValueError("no REFRESH_TOKEN found in environment.")
    if app_key is missing:
        if "APP_KEY" in os.environ:
            app_key = os.environ["APP_KEY"]
        else:
            raise ValueError("no APP_KEY found in environment.")
    if app_secret is missing:
        if "APP_SECRET" in os.environ:
            app_secret = os.environ["APP_SECRET"]
        else:
            raise ValueError("no APP_SECRET found in environment.")

    dbx = dropbox.Dropbox(oauth2_refresh_token=refresh_token, app_key=app_key, app_secret=app_secret, **kwargs)
    try:
        dbx.files_list_folder(path="")  # just to test proper credentials
    except dropbox.exceptions.AuthError:
        raise ValueError("invalid dropbox credentials")


def _login_dbx():
    if dbx is None:
        dropbox_init()  # use environment


def list_dropbox(path="", recursive=False, show_files=True, show_folders=False):
    """
    list_dropbox

    returns all dropbox files/folders in path

    Parameters
    ----------
    path : str or Pathlib.Path
        path from which to list all files (default: '')

    recursive : bool
        if True, recursively list files. if False (default) no recursion

    show_files : bool
        if True (default), show file entries
        if False, do not show file entries

    show_folders : bool
        if True, show folder entries
        if False (default), do not show folder entries

    Returns
    -------
    files : list

    Note
    ----
    Directory entries are never returned

    Note
    ----
    If REFRESH_TOKEN, APP_KEY and APP_SECRET environment variables are specified,
    it is not necessary to call dropbox_init() prior to any dropbox function.
    """
    _login_dbx()
    out = []
    result = dbx.files_list_folder(path, recursive=recursive)

    for entry in result.entries:
        if show_files and isinstance(entry, dropbox.files.FileMetadata):
            out.append(entry.path_display)
        if show_folders and isinstance(entry, dropbox.files.FolderMetadata):
            out.append(entry.path_display + "/")

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        for entry in result.entries:
            if show_files and isinstance(entry, dropbox.files.FileMetadata):
                out.append(entry.path_display)
            if show_folders and isinstance(entry, dropbox.files.FolderMetadata):
                out.append(entry.path_display + "/")

    return out


def read_dropbox(dropbox_path, max_retries=100):
    """
    read_dropbox

    read from dopbox at given path

    Parameters
    ----------
    dropbox_path : str or Pathlib.Path
        path to read from

    max_retries : int
        number of retries (default: 100)

    Returns
    -------
    contents of the dropbox file : bytes

    Note
    ----
    If REFRESH_TOKEN, APP_KEY and APP_SECRET environment variables are specified,
    it is not necessary to call dropbox_init() prior to any dropbox function.

    As reading from dropbox is very unreliable under pyodide, reading will have to be retried (by default maximum 100 times).
    The number of retries can be found with read_dropbox.retries
    """

    _login_dbx()
    for read_dropbox.retries in range(max_retries+1):
        metadata, response = dbx.files_download(dropbox_path)
        file_content = response.content
        if len(file_content) == metadata.size:
            return file_content
    raise OSError(f"after {max_retries} still no valid response")

def write_dropbox(dropbox_path, contents):
    _login_dbx()
    """
    write_dropbox
    
    write from dopbox at given path
    
    Parameters
    ----------
    dropbox_path : str or Pathlib.Path
        path to write to

    contents : bytes
        contents to be written
        
    Note
    ----
    If REFRESH_TOKEN, APP_KEY and APP_SECRET environment variables are specified,
    it is not necessary to call dropbox_init() prior to any dropbox function.
    """
    dbx.files_upload(contents, dropbox_path, mode=dropbox.files.WriteMode.overwrite)


def list_local(path, recursive=False, show_files=True, show_folders=False):
    """
    list_local

    returns all local files/folders in path

    Parameters
    ----------
    path : str or Pathlib.Path
        path from which to list all files (default: '')

    recursive : bool
        if True, recursively list files. if False (default) no recursion

    show_files : bool
        if True (default), show file entries
        if False, do not show file entries

    show_folders : bool
        if True, show folder entries
        if False (default), do not show folder entries

    Returns
    -------
    files, relative to path : list
    """
    path = Path(path)

    result = []
    for entry in path.iterdir():
        if entry.is_file():
            if show_files:
                result.append(str(entry))
        elif entry.is_dir():
            if show_folders:
                result.append(str(entry) + "/")
            if recursive:
                result.extend(list_local(entry, recursive=recursive, show_files=show_files, show_folders=show_folders))
    return result


def write_local(path, contents):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(contents)


def read_local(path):
    path = Path(path)
    with open(path, "rb") as f:
        contents = f.read()
    return contents


class block:
    """
    block is 2 dimensional data structure with 1 as lowest index (like xlwings range)

    Parameters
    ----------
    number_of_rows : int
        number of rows

    number_of_columns : int
        number of columns

    Returns
    -------
    block
    """

    def __init__(self, value=missing, *, number_of_rows=missing, number_of_columns=missing, column_like=False):
        self.dict = {}
        self.column_like = column_like
        if value is missing:
            if number_of_rows is missing:
                number_of_rows = 1
            if number_of_columns is missing:
                number_of_columns = 1
            self.number_of_rows = number_of_rows
            self.number_of_columns = number_of_columns

        else:
            if isinstance(value, block):
                value = value.value
            self.value = value
            if number_of_rows is not missing:
                self.number_of_rows = number_of_rows
            if number_of_columns is not missing:
                self.number_of_columns = number_of_columns

    @classmethod
    def from_xlrd_sheet(cls, sheet, number_of_rows=missing, number_of_columns=missing):
        v = [sheet.row_values(row_idx)[0 : sheet.ncols] for row_idx in range(0, sheet.nrows)]
        return cls(v, number_of_rows=number_of_rows, number_of_columns=number_of_columns)

    @classmethod
    def from_openpyxl_sheet(cls, sheet, number_of_rows=missing, number_of_columns=missing):
        v = [[cell.value for cell in row] for row in sheet.iter_rows()]
        return cls(v, number_of_rows=number_of_rows, number_of_columns=number_of_columns)

    @classmethod
    def from_file(cls, filename, number_of_rows=missing, number_of_columns=missing):
        with open(filename, "r") as f:
            v = [[line if line else missing] for line in f.read().splitlines()]
        return cls(v, number_of_rows=number_of_rows, number_of_columns=number_of_columns)

    @classmethod
    def from_dataframe(cls, df, number_of_rows=missing, number_of_columns=missing):
        v = df.values.tolist()
        return cls(v, number_of_rows=number_of_rows, number_of_columns=number_of_columns)

    def to_openpyxl_sheet(self, sheet):
        for row in self.value:
            sheet.append(row)

    @property
    def value(self):
        return [[self.dict.get((row, column)) for column in range(1, self.number_of_columns + 1)] for row in range(1, self.number_of_rows + 1)]

    @value.setter
    def value(self, value):
        if not isinstance(value, list):
            value = [[value]]
        if not isinstance(value[0], list):
            if self.column_like:
                value = [[item] for item in value]
            else:
                value = [value]

        self.number_of_rows = len(value)
        self._number_of_columns = 0

        for row, row_contents in enumerate(value, 1):
            for column, item in enumerate(row_contents, 1):
                if item and not (isinstance(item, float) and math.isnan(item)):
                    self.dict[row, column] = item
                    self._number_of_columns = max(self.number_of_columns, column)

    def __setitem__(self, row_column, value):
        row, column = row_column
        if row < 1 or row > self.number_of_rows:
            raise IndexError(f"row must be between 1 and {self.number_of_rows} not {row}")
        if column < 1 or column > self.number_of_columns:
            raise IndexError(f"column must be between 1 and {self.number_of_columns} not {column}")
        self.dict[row, column] = value

    def __getitem__(self, row_column):
        row, column = row_column
        if row < 1 or row > self.number_of_rows:
            raise IndexError(f"row must be between 1 and {self.number_of_rows} not {row}")
        if column < 1 or column > self.number_of_columns:
            raise IndexError(f"column must be between 1 and {self.number_of_columns} not {column}")
        return self.dict.get((row, column))

    def minimized(self):
        """
        Returns
        -------
        minimized block : block
             uses highest_used_row_number and highest_used_column_number to minimize the block
        """
        return block(self, number_of_rows=self.highest_used_row_number, number_of_columns=self.highest_used_column_number)

    @property
    def number_of_rows(self):
        return self._number_of_rows

    @number_of_rows.setter
    def number_of_rows(self, value):
        if value < 1:
            raise ValueError(f"number_of_rows should be >=1, not {value}")
        self._number_of_rows = value
        for row, column in list(self.dict):
            if row > self._number_of_rows:
                del self.dict[row, column]

    @property
    def number_of_columns(self):
        return self._number_of_columns

    @number_of_columns.setter
    def number_of_columns(self, value):
        if value < 1:
            raise ValueError(f"number_of_columns should be >=1, not {value}")
        self._number_of_columns = value
        for row, column in list(self.dict):
            if column > self._number_of_columns:
                del self.dict[row, column]

    @property
    def highest_used_row_number(self):
        if self.dict:
            return max(row for (row, column) in self.dict)
        else:
            return 1

    @property
    def highest_used_column_number(self):
        if self.dict:
            return max(column for (row, column) in self.dict)
        else:
            return 1

    def __repr__(self):
        return f"block({self.value})"

    def _check_row(self, row, name):
        if row < 1:
            raise ValueError(f"{name}={row} < 1")
        if row > self.number_of_rows:
            raise ValueError(f"{name}={row} > number_of_rows={self.number_of_rows}")

    def _check_column(self, column, name):
        if column < 1:
            raise ValueError(f"{name}={column} < 1")
        if column > self.number_of_columns:
            raise ValueError(f"{name}={column} > number_of_columns={self.number_of_columns}")

    def vlookup(self, s, *, row_from=1, row_to=missing, column1=1, column2=missing, default=missing):
        """
        searches in column1 for row between row_from and row_to for s and returns the value found at (that row, column2)

        Parameters
        ----------
        s : any
            value to seach for

        row_from : int
             row to start search (default 1)

             should be between 1 and number_of_rows

        row_to : int
             row to end search (default number_of_rows)

             should be between 1 and number_of_rows

        column1 : int
             column to search in (default 1)

             should be between 1 and number_of_columns

        column2 : int
             column to return looked up value from (default column1 + 1)

             should be between 1 and number_of_columns

        default : any
             if s is not found, returns the default.

             if omitted, a ValueError exception will be raised in that case

        Returns
        -------
        block[found row number, column2] : any
        """
        if column2 is missing:
            column2 = column1 + 1
        self._check_column(column2, "column2")
        row = self.lookup_row(s, row_from=row_from, row_to=row_to, column1=column1, default=-1)
        if row == -1:
            if default is missing:
                raise ValueError(f"{s} not found]")
            else:
                return default
        else:
            return self[row, column2]

    def lookup_row(self, s, *, row_from=1, row_to=missing, column1=1, default=missing):
        """
        searches in column1 for row between row_from and row_to for s and returns that row number

        Parameters
        ----------
        s : any
            value to seach for

        row_from : int
             row to start search (default 1)

             should be between 1 and number_of_rows

        row_to : int
             row to end search (default number_of_rows)

             should be between 1 and number_of_rows

        column1 : int
             column to search in (default 1)

             should be between 1 and number_of_columns

        column2 : int
             column to return looked up value from (default column1 + 1)

        default : any
             if s is not found, returns the default.

             if omitted, a ValueError exception will be raised

        default : any
             if s is not found, returns the default.

             if omitted, a ValueError exception will be raised in that case


        Returns
        -------
        row number where block[row nunber, column1] == s : int
        """
        if row_to is missing:
            row_to = self.highest_used_row_number
        self._check_row(row_from, "row_from")
        self._check_row(row_to, "row_to")
        self._check_column(column1, "column1")

        for row in range(row_from, row_to + 1):
            if self[row, column1] == s:
                return row
        if default is missing:
            raise ValueError(f"{s} not found")
        else:
            return default

    def hlookup(self, s, *, column_from=1, column_to=missing, row1=1, row2=missing, default=missing):
        """
        searches in row1 for column between column_from and column_to for s and returns the value found at (that column, row2)

        Parameters
        ----------
        s : any
            value to seach for

        column_from : int
             column to start search (default 1)

             should be between 1 and number_of_columns

        column_to : int
             column to end search (default number_of_columns)

             should be between 1 and number_of_columns

        row1 : int
             row to search in (default 1)

             should be between 1 and number_of_rows

        row2 : int
             row to return looked up value from (default row1 + 1)

             should be between 1 and number_of_rows

        default : any
             if s is not found, returns the default.

             if omitted, a ValueError exception will be raised in that case

        Returns
        -------
        block[row, found column, row2] : any
        """
        if row2 is missing:
            row2 = row1 + 1
        self._check_row(row2, "row2")
        column = self.lookup_column(s, column_from=column_from, column_to=column_to, row1=row1, default=-1)
        if column == -1:
            if default is missing:
                raise ValueError(f"{s} not found")
            else:
                return default
        else:
            return self[row2, column]

    def lookup_column(self, s, *, column_from=1, column_to=missing, row1=1, default=missing):
        """
        searches in row1 for column between column_from and column_to for s and returns that column number

        Parameters
        ----------
        s : any
            value to seach for

        column_from : int
             column to start search (default 1)

             should be between 1 and number_of_columns

        column_to : int
             column to end search (default number_of_columns)

             should be between 1 and number_of_columns

        row1 : int
             row to search in (default 1)

             should be between 1 and number_of_rows

        row2 : int
             row to return looked up value from (default row1 + 1)

        default : any
             if s is not found, returns the default.

             if omitted, a ValueError exception will be raised in that case

        Returns
        -------
        column number where block[row1, column number] == s : int
        """
        if column_to is missing:
            column_to = self.highest_used_column_number
        self._check_column(column_from, "column_from")
        self._check_column(column_to, "column_to")
        self._check_row(row1, "row1")

        for column in range(column_from, column_to + 1):
            if self[row1, column] == s:
                return column
        if default is missing:
            raise ValueError(f"{s} not found")
        else:
            return default

    def lookup(self, s, *, row_from=1, row_to=missing, column1=1, column2=missing, default=missing):
        """
        searches in column1 for row between row_from and row_to for s and returns the value found at (that row, column2)

        Parameters
        ----------
        s : any
            value to seach for

        row_from : int
             row to start search (default 1)

             should be between 1 and number_of_rows

        row_to : int
             row to end search (default number_of_rows)

             should be between 1 and number_of_rows

        column1 : int
             column to search in (default 1)

             should be between 1 and number_of_columns

        column2 : int
             column to return looked up value from (default column1 + 1)

             should be between 1 and number_of_columns

        default : any
             if s is not found, returns the default.

             if omitted, a ValueError exception will be raised in that case

        Returns
        -------
        block[found row number, column2] : any

        Note
        ----
        This is exactly the same as vlookup.
        """
        return self.vlookup(s, row_from=row_from, row_to=row_to, column1=column1, column2=column2, default=default)

    def decode_to_files(self):
        """
        decode the block with encoded file(s) to individual local files
        """
        for column in self.number_of_columns:
            row = 1
            while row <= self.number_of_rows:
                if self[row, column] and self[row, column].startswith("<file=") and self[row, column].endswith(">"):
                    filename = self[row, column][6:-1]
                    collect = []
                    row += 1
                    while self[row, column] != "</file>":
                        print(f"{self[row,column]=}")

                        if self[row, column]:
                            collect.append(self[row, column])
                        row += 1
                    decoded = base64.b64decode("".join(collect))
                    open(filename, "wb").write(decoded)
                row += 1

    @classmethod
    def encode_files(cls, *files):
        """
        make a block with the given files encoded

        Parameters
        ----------
        files : file names (str)
            files to be encoded

        Returns
        -------
        block with encoded files : block
            not minimized!
        """

        bl = cls(number_of_rows=50000, number_of_columns=1)

        n = 5000  # block size
        row = 1
        for file in files:
            bl[row, 1] = f"<file={file}>"
            row += 1
            b64 = base64.b64encode(open(file, "rb").read()).decode("utf-8")
            while b64:
                b64_n = b64[:n]
                bl[row, 1] = b64_n
                row += 1
                b64 = b64[n:]
            bl[row, 1] = f"</file>"
            row += 1
        return bl


class Capture:
    """
    specifies how to capture stdout

    Parameters
    ----------
    enabled : bool
        if True (default), all stdout output is captured

        if False, stdout output is printed

    include_print : bool
        if False (default), nothing will be printed if enabled is True

        if True, output will be printed (and captured if enabled is True)

    Note
    ----
    Use this like ::

        capture = xwu.Capture()
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        # singleton
        if cls._instance is None:
            cls._instance = super(Capture, cls).__new__(cls)
        return cls._instance

    def __init__(self, enabled=missing, include_print=missing):
        if hasattr(self, "stdout"):
            if enabled is not missing:
                self.enabled = enabled
            if include_print is not missing:
                self.include_print = include_print
            return
        self.stdout = sys.stdout
        self._buffer = []
        self.enabled = True if enabled is missing else enabled
        self.include_print = False if include_print is missing else include_print

    def __call__(self, enabled=missing, include_print=missing):
        return self.__class__(enabled, include_print)

    def __enter__(self):
        self.enabled = True

    def __exit__(self, exc_type, exc_value, tb):
        self.enabled = False

    def write(self, data):
        self._buffer.append(data)
        if self._include_print:
            self.stdout.write(data)

    def flush(self):
        if self._include_print:
            self.stdout.flush()
        self._buffer.append("\n")

    @property
    def enabled(self):
        return sys.out == self

    @enabled.setter
    def enabled(self, value):
        if value:
            sys.stdout = self
        else:
            sys.stdout = self.stdout

    @property
    def value(self):
        result = self.value_keep
        self.clear()
        return result

    @property
    def value_keep(self):
        result = [[line] for line in self.str_keep.splitlines()]
        return result

    @property
    def str(self):
        result = self.str_keep
        self._buffer.clear()
        return result

    @property
    def str_keep(self):
        result = "".join(self._buffer)
        return result

    def clear(self):
        self._buffer.clear()

    @property
    def include_print(self):
        return self._include_print

    @include_print.setter
    def include_print(self, value):
        self._include_print = value

def trigger_macro(sheet):
    """
    triggers the macro on sheet

    Parameters
    ----------
    sheet : sheet
        sheet to use

    """

    sheet["A1"].value = "=NOW()"


if __name__ == "__main__":
    ...

