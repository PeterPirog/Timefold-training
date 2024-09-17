from typing import Dict
from subprocess import CompletedProcess, run
import pandas as pd
pd.set_option("display.max_columns", None)
from pandas import DataFrame, read_csv
from os.path import join, splitext, basename
from os import remove
import tools.settings
import os


def construct_csv_path(dbase_file_path: str) -> str:
    """
    Konstrukcja ścieżki do pliku CSV na podstawie ścieżki do pliku DBF.
    """
    csv_file_name = splitext(basename(dbase_file_path))[0] + '.csv'
    return join(tools.settings.CSV_FILES_PATH, csv_file_name)


def is_file_locked(filepath: str) -> bool:
    """Sprawdza, czy plik jest zablokowany przez inny proces."""
    try:
        with open(filepath, 'r+'):
            return False
    except IOError:
        return True

def execute_odbc_script(dbase_file_path: str, python_interpreter_path: str, script_path: str) -> CompletedProcess:
    """
    Wykonuje skrypt ODBC i zwraca wynik procesu.
    """
    command_parameters = [python_interpreter_path, script_path, f'dbf_file_path={dbase_file_path}']
    process = run(command_parameters, capture_output=True, text=True)
    if process.returncode != 0:
        print(f"Skrypt ODBC zwrócił błąd: {process.stderr}")
    else:
        print(f"Skrypt ODBC wykonany poprawnie. {process.stdout}")
    return process


def parse_ODBC_to_df(dbase_file_path: str, python_interpreter_path: str = tools.settings.PYTHON_32BIT_INTERPRETER,
                     script_path: str = tools.settings.ODBC_READ_SCRIPT_PATH,
                     remove_csv_after_read: bool = True) -> DataFrame:
    """
    Parsowanie danych z ODBC do obiektu DataFrame Pandas. Obsługuje błędy dostępu do plików.
    """
    csv_file_path = construct_csv_path(dbase_file_path)

    # Sprawdzenie dostępności pliku DBF
    try:
        if not os.path.isfile(dbase_file_path):
            raise FileNotFoundError(f"Plik DBF nie został znaleziony: {dbase_file_path}")

        # Sprawdzenie, czy plik jest zablokowany
        if is_file_locked(dbase_file_path):
            raise PermissionError(f"Plik DBF '{dbase_file_path}' jest zablokowany przez inny proces.")

        if not os.access(dbase_file_path, os.R_OK):
            raise PermissionError(f"Plik DBF '{dbase_file_path}' jest niedostępny do odczytu.")

        # Wykonanie skryptu ODBC
        result = execute_odbc_script(dbase_file_path, python_interpreter_path, script_path)
        if result.returncode != 0:
            print(f"Skrypt ODBC nie powiódł się: {result.stderr}")
            raise RuntimeError(f"Skrypt ODBC zakończył się kodem {result.returncode}")

    except PermissionError as pe:
        print(f"Błąd dostępu do pliku: {pe}")
        raise

    except FileNotFoundError as fe:
        print(f"Plik DBF nie został znaleziony lub jest niedostępny: {fe}")
        raise

    # Sprawdzenie dostępności pliku CSV
    try:
        if not os.path.isfile(csv_file_path):
            raise FileNotFoundError(f"Plik CSV nie został znaleziony: {csv_file_path}. Skrypt ODBC mógł nie wygenerować pliku CSV.")

        dtype: Dict[str, str] = {col: str for col in tools.settings.STRING_COLUMN_LIST}
        df = read_csv(csv_file_path, dtype=dtype, low_memory=False)

    except FileNotFoundError as fnf_error:
        print(f"Plik CSV nie został znaleziony: {csv_file_path}. Skrypt ODBC mógł nie wygenerować pliku CSV.")
        raise fnf_error
    except PermissionError as pe:
        print(f"Plik CSV '{csv_file_path}' jest zablokowany przez inny proces i nie można go otworzyć.")
        raise pe
    except Exception as e:
        print(f"Nie udało się załadować pliku CSV: {e}")
        raise

    # Konwersja kolumn do typów numerycznych
    df = convert_columns_to_numeric(df, tools.settings.NUMERIC_COLUMN_LIST)

    # Konwersja kolumn do typów daty i czasu
    df = convert_columns_to_date(df, tools.settings.DATE_COLUMN_LIST, tools.settings.DATETIME_COLUMN_LIST)

    # Usunięcie pliku CSV po przetworzeniu
    if remove_csv_after_read:
        try:
            remove(csv_file_path)
        except Exception as e:
            print(f"Nie udało się usunąć pliku CSV: {e}")

    return df.drop_duplicates()


def convert_columns_to_numeric(df: DataFrame, column_list: list) -> DataFrame:
    """
    Konwertuje podane kolumny w DataFrame na typy numeryczne.
    """
    for column in column_list:
        if column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column], errors='coerce')
            except ValueError as ve:
                print(f"Nie udało się przekonwertować kolumny {column} na typ numeryczny: {ve}")
    return df


def convert_columns_to_date(df: DataFrame, date_columns_list: list, datetime_column_list: list) -> DataFrame:
    """
    Konwertuje podane kolumny w DataFrame na typy daty i czasu.
    Obsługuje nieprawidłowe formaty i przekroczenia zakresu dat.
    """
    for column in df.columns:
        if column in date_columns_list:
            try:
                df[column] = pd.to_datetime(df[column], format='%Y-%m-%d', errors='coerce').dt.date
            except ValueError as ve:
                print(f"Nie udało się przekonwertować kolumny {column} na typ daty: {ve}")

        elif column in datetime_column_list:
            try:
                df[column] = pd.to_datetime(df[column], errors='coerce')
            except ValueError as ve:
                print(f"Nie udało się przekonwertować kolumny {column} na typ daty/czasu: {ve}")

        # Zamiana NaT na None
        df[column] = df[column].where(pd.notnull(df[column]), None)

        # Zamiana konkretnej wartości '1899-12-30' na None
        if column in datetime_column_list:
            df[column] = df[column].apply(lambda x: None if x == pd.Timestamp('1899-12-30 00:00:00') else x)
        elif column in date_columns_list:
            df[column] = df[column].apply(lambda x: None if x == pd.Timestamp('1899-12-30').date() else x)

    return df


if __name__ == '__main__':
    try:
        dbase_file_path_example = r'G:\PycharmProject\Timefold-training\Logis\DANE\ksiazka_k.DBF'
        df_example = parse_ODBC_to_df(dbase_file_path_example, remove_csv_after_read=True)

        print(df_example.head())
        print(df_example.info())
    except Exception as e:
        print("Główna część programu nie powiodła się:", e)
        raise
