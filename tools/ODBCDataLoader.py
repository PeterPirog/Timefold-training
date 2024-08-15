from typing import Dict
import pandas as pd
from pandas import DataFrame
from tools.DBF_Reader_ODBC import parse_ODBC_to_df
from tools.settings import DBF_PATHS, PYTHON_32BIT_INTERPRETER, ODBC_READ_SCRIPT_PATH, DATE_COLUMN_LIST

pd.set_option("display.max_columns", None)

class DataLoader:
    """
    DataLoader is a class that loads and updates data from ODBC based on keys defined in DBF_PATHS.
    """

    def __init__(self):
        """
        DataLoader constructor. Initializes an empty dictionary for storing loaded data
        and generates properties for all keys defined in DBF_PATHS.
        """
        self._loaded_data: Dict[str, DataFrame] = {}
        self._generate_properties()

    def _load_data_if_not_loaded(self, key: str) -> DataFrame:
        """
        Loads data for a specific key if it hasn't been loaded yet.
        :param key: key for which to load data.
        :return: Loaded data as DataFrame.
        """
        if key not in self._loaded_data:
            self._loaded_data[key] = self._fetch_data(key)
        return self._loaded_data[key]

    def _generate_properties(self):
        """
        Generates a property for each key in DBF_PATHS. Each property is associated with a data load function.
        """
        for key in DBF_PATHS:
            setattr(self.__class__, key, property(lambda self, key=key: self._load_data_if_not_loaded(key)))

    def _format_date_columns(self, df: DataFrame, date_column_list: list) -> DataFrame:
        """
        Formats the date columns in a DataFrame.
        :param df: DataFrame in which to format date columns.
        :param date_column_list: List of date columns to format.
        :return: DataFrame with formatted date columns.
        """
        for column in date_column_list:
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], format="%Y-%m-%d %H:%M:%S", errors='coerce')
        return df

    def _fetch_data(self, key: str) -> DataFrame:
        """
        Fetches data for a specific key using ODBC.
        :param key: Key for which to fetch data.
        :return: Fetched data as DataFrame.
        """
        print(f"Fetching {key} from {DBF_PATHS[key]} using ODBC...")
        try:
            df = parse_ODBC_to_df(
                dbase_file_path=DBF_PATHS[key],
                python_interpreter_path=PYTHON_32BIT_INTERPRETER,
                script_path=ODBC_READ_SCRIPT_PATH
            )
            return self._format_date_columns(df, DATE_COLUMN_LIST)
        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot find the specified file: {DBF_PATHS[key]}")
        except Exception as e:
            raise RuntimeError(f"Error occurred while fetching data for {key}: {str(e)}")

    def refresh_data(self):
        """
        Refreshes all loaded data using ODBC.
        """
        for key in self._loaded_data:
            print(f"Refreshing {key} from {DBF_PATHS[key]} using ODBC...")
            self._loaded_data[key] = self._fetch_data(key)


if __name__ == '__main__':
    data_loader = DataLoader()

    ksiazka_k_df: DataFrame = data_loader.ksiazka_k
    print(ksiazka_k_df.head())

    data_loader.refresh_data()

    updated_ksiazka_k_df: DataFrame = data_loader.ksiazka_k
    print(updated_ksiazka_k_df.head())
    print(updated_ksiazka_k_df.info())
