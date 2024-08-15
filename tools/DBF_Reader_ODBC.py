from subprocess import CompletedProcess, run
from pandas import DataFrame, read_csv
from os.path import join, splitext, basename

import tools.settings


def construct_csv_path(dbase_file_path: str) -> str:
    """
    Constructs a path for a CSV file from a given DBASE file path.

    :param dbase_file_path: The filepath of a DBASE file
    :return: The constructed CSV file path
    :raises Exception: If an error occurred while constructing the CSV file path
    """
    try:
        csv_file_name = splitext(basename(dbase_file_path))[0] + '.csv'
        return join(tools.settings.CSV_FILES_PATH, csv_file_name)
    except Exception as e:
        print("Failed to construct CSV file path:", e)
        raise


def execute_odbc_script(dbase_file_path: str, python_interpreter_path: str, script_path: str) -> CompletedProcess:
    """
    Executes an ODBC script given certain parameters.

    :param dbase_file_path: The filepath of a DBASE file
    :param python_interpreter_path: The filepath of a Python interpreter
    :param script_path: The filepath of a script to be executed
    :return: The result of the executed script
    :raises Exception: If an error occurred while executing the ODBC script
    """
    try:
        command_parameters = [python_interpreter_path, script_path, f'dbf_file_path={dbase_file_path}']
        return run(command_parameters, capture_output=True, text=True)
    except Exception as e:
        print("Failed to execute ODBC script:", e)
        raise


def parse_ODBC_to_df(dbase_file_path: str, python_interpreter_path: str = tools.settings.PYTHON_32BIT_INTERPRETER,
                     script_path: str = tools.settings.ODBC_READ_SCRIPT_PATH) -> DataFrame:
    """
    Transforms a DBASE file located at a specified path to a pandas DataFrame using ODBC.

    :param dbase_file_path: The filepath of a DBASE file
    :param python_interpreter_path: The filepath of a Python interpreter
    :param script_path: The filepath of an ODBC read script to be executed
    :return: A pandas DataFrame representing the content of the DBASE file
    :raises Exception: If an error occurred while parsing DBF to DataFrame
    """
    try:
        csv_file_path = construct_csv_path(dbase_file_path)
        print(f'dbase_file_path={dbase_file_path}')
        result = execute_odbc_script(dbase_file_path, python_interpreter_path, script_path)
        if result.returncode != 0:
            print("ODBC script execution failed with output:", result.stderr)
        return read_csv(csv_file_path)
    except Exception as e:
        print("Failed to parse DBF to DataFrame:", e)
        raise


if __name__ == '__main__':
    """
    A main function that provides an example of how to use parse_ODBC_to_df function.

    Raises Exception - if an error occurred during the execution of the main function.
    """
    try:
        dbase_file_path_example = r'D:\PycharmProjects\django-odbc\Logis\DANE\ksiazka_k.DBF'
        df_example = parse_ODBC_to_df(dbase_file_path_example)

        print(df_example.head())
        print(df_example.info())
    except Exception as e:
        print("Main program execution failed:", e)
        raise
