from typing import Dict
import pandas as pd
pd.set_option("display.max_rows", None)
from pandas import DataFrame
from optylogisdep.modules.timefold_optimizer.tools.DBF_Reader_ODBC import parse_ODBC_to_df
from optylogisdep.modules.timefold_optimizer.tools.settings import DBF_PATHS, PYTHON_32BIT_INTERPRETER, ODBC_READ_SCRIPT_PATH, DATE_COLUMN_LIST, DATETIME_COLUMN_LIST

pd.set_option("display.max_columns", None)


class DataLoader:
    """
    Class DataLoader automates the loading and updating of data from an ODBC datasource.
    The class uses the keys defined in the DBF_PATHS to identify the data to be loaded.
    """

    def __init__(self, remove_csv_after_read=True):
        """
        Constructor for the DataLoader class.

        Params:
        remove_csv_after_read: boolean, if true the csv file will be deleted after data extraction.
        """
        self.remove_csv_after_read = remove_csv_after_read
        self._loaded_data: Dict[str, DataFrame] = {}
        self._generate_properties()

    def _load_data_if_not_loaded(self, key: str) -> DataFrame:
        """
        Ensures data is loaded for a specific key if it isn't already loaded.

        Params:
        key: str, the key for the data to be loaded.

        Returns:
        Loaded DataFrame corresponding to the key.
        """
        if key not in self._loaded_data:
            self._loaded_data[key] = self._fetch_data(key)
        return self._loaded_data[key]

    def _generate_properties(self):
        """
        Creates properties for each key in DBF_PATHS.
        These properties are linked with a function to load the associated data.
        """
        for key in DBF_PATHS:
            setattr(self.__class__, key, property(lambda self, key=key: self._load_data_if_not_loaded(key)))

    def _format_date_columns(self, df: DataFrame) -> DataFrame:
        """
        Formats the date columns in the given DataFrame based on whether they are in the day or hour list.

        Params:
        df: DataFrame, the dataframe to format.

        Returns:
        DataFrame where the date columns have been formatted.
        """
        for column in df.columns:
            if column in DATE_COLUMN_LIST:
                df[column] = pd.to_datetime(df[column], format='%Y-%m-%d', errors='coerce')
            elif column in DATETIME_COLUMN_LIST:
                df[column] = pd.to_datetime(df[column], format='%Y-%m-%d %H:%M:%S', errors='coerce')
        return df

    def _fetch_data(self, key: str) -> DataFrame:
        """
        Retrieves data for a given key through ODBC.

        Params:
        key: str, the key to fetch data for.

        Returns:
        DataFrame that contains fetched data based on the key.

        Raises:
        FileNotFoundError if the specified file cannot be found.
        RuntimeError if an error occurred while fetching data.
        """
        print(f"Fetching {key} from {DBF_PATHS[key]} using ODBC...")
        try:
            df = parse_ODBC_to_df(
                dbase_file_path=DBF_PATHS[key],
                python_interpreter_path=PYTHON_32BIT_INTERPRETER,
                script_path=ODBC_READ_SCRIPT_PATH,
                remove_csv_after_read=self.remove_csv_after_read
            )
            return self._format_date_columns(df)
        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot find the specified file: {DBF_PATHS[key]}")
        except Exception as e:
            raise RuntimeError(f"Error occurred while fetching data for {key}: {str(e)}")

    def refresh_data(self):
        """
        Updates all currently loaded data through the ODBC datasource.
        """
        for key in self._loaded_data:
            print(f"Refreshing {key} from {DBF_PATHS[key]} using ODBC...")
            self._loaded_data[key] = self._fetch_data(key)


if __name__ == '__main__':
    data_loader = DataLoader(remove_csv_after_read=True)
    # ksiazka_k_df = data_loader.ksiazka_k
    # print(ksiazka_k_df.head())

    bok_df = data_loader.bok
    #print(bok_df.head())
   # print(bok_df.info())

    # Print rows in column 'bk_id' where there is a dot '.' in the string
    dot_rows = bok_df[bok_df['bk_id'].astype(str).str.contains('2022-031BK12190')]
    print(dot_rows)
