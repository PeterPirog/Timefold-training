"""
This script is designed to be run with a 32-bit Python interpreter. This is because it relies on the 32-bit ODBC Driver for Visual Fox Pro.
The script has been successfully tested with Python 3.10.0 (tags/v3.10.0:b494f59, Oct  4 2021, 18:46:30) [MSC v.1929 32 bit (Intel)] on a win32 system.

A virtual environment (venv) with the following 32-bit packages is required to run this script:

Package           Version
--------------    -------
pip               24.2
pip-autoremove    0.10.0
pluggy            1.5.0
pyodbc            5.1.0
setuptools        72.2.0
tomli             2.0.1
wheel             0.44.0

Please ensure that these packages are installed within your active Python environment before attempting to run this script.

Additionally, the pandas package, which is used for data manipulation and analysis, needs to be installed globally for 64-bits in the venv environment. This dependency exists because pandas does not run on 32-bit python, and we need to leverage its powerful data analysis and manipulation capabilities.
"""
from typing import Optional, Dict
import os
import csv
import pyodbc
import sys
import settings
import logging

logging.basicConfig(level=logging.DEBUG)


def establish_dbf_connection(connection_data: str) -> pyodbc.Connection:
    """
    Establish a new connection using the provided connection string.

    The function takes a connection string as input, it then establishes
    a new connection and returns it.

    Parameters
    ----------
    connection_data : str
        The connection string to create connection with.
    """
    try:
        connection = pyodbc.connect(connection_data)
        logging.info("Connection established successfully.")
        return connection
    except Exception as e:
        logging.error(f"Error establishing connection: {e}")
        raise


def perform_sql_query(connection_object: pyodbc.Connection, sql_code: str) -> Optional[list[Dict]]:
    """
    Executes a SQL query on the given connection and return pulled data.

    It performs a SQL query on the provided connection object and returns the result
    as a list of dictionaries.

    Parameters
    ----------
    connection_data : pyodbc.Connection
        The connection object to execute the SQL query on.
    sql_code : str
        The SQL code to execute.
    """
    try:
        db_cursor = connection_object.cursor()
        db_cursor.execute(sql_code)
        result_columns = [column[0] for column in db_cursor.description]
        result_data = [dict(zip(result_columns, row)) for row in db_cursor.fetchall()]
        return result_data
    except MemoryError as mem_err:
        logging.error(f"MemoryError: {mem_err}")
        return None
    except Exception as e:
        logging.error(f"Error performing SQL query: {e}")
        raise


def extract_dbf_file_details(dbf_file_location: str) -> tuple[str, str]:
    """
    Extract directory information and table name from .dbf file location.

    This function takes a file location as input and extracts dir information
    and table name from it.

    Parameters
    ----------
    dbf_file_location : str
        The file location to extract information from.
    """
    try:
        dbf_dir = os.path.dirname(dbf_file_location)
        base_name = os.path.basename(dbf_file_location)
        dbf_table_name = os.path.splitext(base_name)[0]
        connection_data = settings.CONNECTION_STRING.format(directory=dbf_dir)
        return dbf_table_name, connection_data
    except Exception as e:
        logging.error(f"Error extracting DBF file details: {e}")
        raise


def convert_dbf_to_dict_list(dbf_file_location: str) -> Optional[list[Dict]]:
    """
    Convert a .dbf file to a list of dictionaries using ODBC.

    This function takes a .dbf file location as an input and converts it into a list
    of dictionaries using ODBC.

    Parameters
    ----------
    dbf_file_location : str
        The .dbf file location to convert.
    """
    try:
        table_name, connection_data = extract_dbf_file_details(dbf_file_location)
        sql_code = f'SELECT * FROM {table_name}'
        connection_object = establish_dbf_connection(connection_data)
        with connection_object:
            extracted_data = perform_sql_query(connection_object, sql_code)
        return extracted_data
    except Exception as e:
        logging.error(f"Error converting DBF to dict list: {e}")
        raise


def trim_string_data(raw_data: list[Dict]) -> list[Dict]:
    """
    Remove leading and trailing spaces of string data in each record of raw data.

    This function takes a list of dictionary records as input and removes leading and
    trailing spaces from string data.

    Parameters
    ----------
    raw_data : list[Dict]
        The raw data to trim string data from.
    """
    try:
        trimmed_data = [{field: (value.strip() if isinstance(value, str) else value)
                         for field, value in single_record.items()}
                        for single_record in raw_data]
        return trimmed_data
    except Exception as e:
        logging.error(f"Error trimming string data: {e}")
        raise


def write_dict_list_to_csv_chunked(data_list: list[dict], csv_file_location: str, chunk_limit: int = 10000):
    """
    Write a list of dictionaries to a CSV file in chunks to prevent memory errors.

    This function takes a list of dictionaries, a csv file location and a chunk limit.
    It then writes the data into the file in chunks according to the provided limit.

    Parameters
    ----------
    data_list : list[dict]
        The data to write to CSV file.
    csv_file_location : str
        The location of the CSV file to write data into.
    chunk_limit : int
        The limit of chunks to write at a time, 10000 by default
    """

    try:
        csv_dir = os.path.dirname(csv_file_location)
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
            logging.info(f"Directory {csv_dir} created.")

        if not data_list:
            logging.info("Data list is empty, CSV file will not be created.")
            return

        with open(csv_file_location, 'w', newline='', encoding='utf-8') as file:
            dict_keys = data_list[0].keys()
            csv_writer = csv.DictWriter(file, fieldnames=dict_keys, escapechar='\\')
            csv_writer.writeheader()

            for i in range(0, len(data_list), chunk_limit):
                chunk = data_list[i:i + chunk_limit]
                csv_writer.writerows(chunk)

        logging.info(f"Wrote data to CSV file at location: {csv_file_location}")
    except Exception as e:
        logging.error(f"Error creating/writing to CSV file: {e}")
        raise


if __name__ == '__main__':
    """
    The main function validates command line arguments and run a series of function accordingly.
    
    It expects a valid path to DBF file via command line arguments, and performs necessary 
    transformations and write the final output to the CSV file.
    """
    try:
        if len(sys.argv) <= 1 or not sys.argv[1].strip():
            raise ValueError('Please provide a path to the DBF file via the command line.')

        sys_arg_split = sys.argv[1].split('=')
        dbf_file_location = sys_arg_split[1]

        if not dbf_file_location or not dbf_file_location.strip():
            raise ValueError('The DBF file location provided cannot be empty.')

        if not os.path.exists(dbf_file_location):
            raise FileNotFoundError(f'The DBF file at path "{dbf_file_location}" does not exist.')

        csv_file_location = os.path.abspath(os.path.join(settings.CSV_FILES_PATH,
                                                         f"{os.path.splitext(os.path.basename(dbf_file_location))[0]}.csv"))

        raw_data = convert_dbf_to_dict_list(dbf_file_location=dbf_file_location)
        if raw_data is not None:
            trimmed_data = trim_string_data(raw_data)
            write_dict_list_to_csv_chunked(trimmed_data, csv_file_location)
        else:
            logging.info("DBF to dictionary conversion resulted in None, no CSV file will be created.")
    except Exception as e:
        logging.error(f"Error running script: {e}")
