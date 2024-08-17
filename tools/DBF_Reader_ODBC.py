from typing import Dict
from subprocess import CompletedProcess, run
import pandas as pd
from pandas import DataFrame, read_csv
from os.path import join, splitext, basename
from os import remove

import tools.settings


def construct_csv_path(dbase_file_path: str) -> str:
    """
    Constructs a CSV file path given a database file path.

    :param dbase_file_path: The database file path.
    :return: The constructed CSV file path.
    """
    try:
        csv_file_name = splitext(basename(dbase_file_path))[0] + '.csv'
        return join(tools.settings.CSV_FILES_PATH, csv_file_name)
    except Exception as e:
        print("Failed to construct CSV file path:", e)
        raise


def execute_odbc_script(dbase_file_path: str, python_interpreter_path: str, script_path: str) -> CompletedProcess:
    """
    Executes an ODBC script.

    :param dbase_file_path: The database file path.
    :param python_interpreter_path: The Python interpreter path.
    :param script_path: The script path.
    :return: The completed process.
    """
    try:
        command_parameters = [python_interpreter_path, script_path, f'dbf_file_path={dbase_file_path}']
        return run(command_parameters, capture_output=True, text=True)
    except Exception as e:
        print("Failed to execute ODBC script:", e)
        raise


def parse_ODBC_to_df(dbase_file_path: str, python_interpreter_path: str = tools.settings.PYTHON_32BIT_INTERPRETER,
                     script_path: str = tools.settings.ODBC_READ_SCRIPT_PATH,
                     remove_csv_after_read: bool = True) -> DataFrame:
    """
    Parses an ODBC to a dataframe.

    :param dbase_file_path: The database file path.
    :param python_interpreter_path: The Python interpreter path. (Default = tools.settings.PYTHON_32BIT_INTERPRETER)
    :param script_path: The script path. (Default = tools.settings.ODBC_READ_SCRIPT_PATH)
    :param remove_csv_after_read: Flag to remove CSV file after reading. (Default = True)
    :return: The parsed dataframe.
    """
    try:
        csv_file_path = construct_csv_path(dbase_file_path)
        print(f'dbase_file_path={dbase_file_path}')

        result = execute_odbc_script(dbase_file_path, python_interpreter_path, script_path)
        if result.returncode != 0:
            print("ODBC script execution failed with output:", result.stderr)

        dtype: Dict[str, str] = {col: str for col in tools.settings.STRING_COLUMN_LIST}
        df = read_csv(csv_file_path, dtype=dtype)

        # Convert columns to float or int if it is in settings.NUMERIC_COLUMN_LIST
        for column in tools.settings.NUMERIC_COLUMN_LIST:
            if column in df.columns:
                try:
                    df[column] = pd.to_numeric(df[column])
                except ValueError as ve:
                    print(f"Failed to convert column {column} to numeric data type:", ve)

        # Remove CSV file after reading if the flag is set
        if remove_csv_after_read:
            remove(csv_file_path)

        return df
    except Exception as e:
        print("Failed to parse DBF to DataFrame:", e)
        raise


if __name__ == '__main__':
    try:
        dbase_file_path_example = r'G:\PycharmProject\Timefold-training\Logis\DANE\pers_st.DBF'
        df_example = parse_ODBC_to_df(dbase_file_path_example, remove_csv_after_read=True)

        print(df_example.head())
        print(df_example.info())
    except Exception as e:
        print("Main program execution failed:", e)
        raise