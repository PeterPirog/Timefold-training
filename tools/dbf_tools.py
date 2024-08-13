import os
import pandas as pd
from pandas.api.types import is_string_dtype
from dbfread import DBF
from dbf import Table
from tools.settings import LOGIS_DIRECTORY, DATE_COLUM_LIST

pd.set_option("display.max_columns", None)



def strip_string_columns(df):
    """Remove leading and trailing spaces from string columns."""
    for column in df.columns:
        if is_string_dtype(df[column]):
            df[column] = df[column].str.strip()
    return df

def convert_date_columns(df, date_column_list):
    for column in date_column_list:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')
    return df


def dbf_to_df(dbf_file_path, date_column_list):
    """Load a DBF file into a DataFrame, convert date columns, and strip strings."""
    table = DBF(dbf_file_path,encoding='ansi',load=True,ignore_missing_memofile=True,ignorecase=True)
    df = pd.DataFrame(iter(table))
    df = strip_string_columns(df)  # Strip leading and trailing spaces
    df = convert_date_columns(df, date_column_list)
    return df

"""

pers_gr = dbf_to_df(dbf_file_path=pers_gr_file_path)

if __name__ == '__main__':
    pers_gr = dbf_to_df(dbf_file_path=pers_gr_file_path)
    print(pers_gr.info())  # Verify the data types of the columns
    print(pers_gr)
"""