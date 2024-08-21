from typing import Dict
from subprocess import CompletedProcess
from os.path import join, splitext, basename
from os import remove
import pandas as pd
pd.set_option("display.max_columns", None)
from pandas import DataFrame, read_csv
from subprocess import run
import os

from optylogisdep.modules.timefold_optimizer.tools import settings


def construct_csv_path(dbase_file_path: str) -> str:
    csv_file_name = splitext(basename(dbase_file_path))[0] + '.csv'
    return join(settings.CSV_FILES_PATH, csv_file_name)


def execute_odbc_script(dbase_file_path: str, python_interpreter_path: str, script_path: str) -> CompletedProcess:
    command_parameters = [python_interpreter_path, script_path, f'dbf_file_path={dbase_file_path}']
    return run(command_parameters, capture_output=True, text=True)


def parse_ODBC_to_df(dbase_file_path: str, python_interpreter_path: str = settings.PYTHON_32BIT_INTERPRETER,
                     script_path: str = settings.ODBC_READ_SCRIPT_PATH,
                     remove_csv_after_read: bool = True) -> DataFrame:
    csv_file_path = construct_csv_path(dbase_file_path)
    print(f'dbase_file_path={dbase_file_path}')

    result = execute_odbc_script(dbase_file_path, python_interpreter_path, script_path)
    if result.returncode != 0:
        print("ODBC script execution failed with output:", result.stderr)

    dtype: Dict[str, str] = {col: str for col in settings.STRING_COLUMN_LIST}

    df = read_csv(csv_file_path, dtype=dtype)
    df = convert_columns_to_numeric(df, settings.NUMERIC_COLUMN_LIST)
    df = convert_columns_to_date(df, settings.DATE_COLUMN_LIST)

    if remove_csv_after_read:
        remove(csv_file_path)

    return df.drop_duplicates()


def convert_columns_to_numeric(df: DataFrame, column_list: list) -> DataFrame:
    for column in column_list:
        if column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except ValueError as ve:
                print(f"Failed to convert column {column} to numeric data type:", ve)
    return df


def convert_columns_to_date(df: DataFrame, column_list: list) -> DataFrame:
    for column in column_list:
        if column in df.columns:
            try:
                df[column] = pd.to_datetime(df[column], format='%Y-%m-%d')
            except ValueError as ve:
                print(f"Failed to convert column {column} to date data type:", ve)
    return df


if __name__ == '__main__':
    try:
        dbase_file_path_example = os.path.abspath(os.path.join(settings.PROJECT_ROOT, 'Logis', 'DANE', 'bok.DBF'))
        df_example = parse_ODBC_to_df(dbase_file_path_example, remove_csv_after_read=False)

        print(df_example.head())
        print(df_example.info())
    except Exception as e:
        print("Main program execution failed:", e)
        raise
