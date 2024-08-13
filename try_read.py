"""


from tools.db_dataframes import Logis

logis=Logis()
#print(logis.pers_gr.info())
print(logis.bok)

"""
import pandas as pd
import dbf

def dbf_to_df(dbf_file_path):
    # Open the DBF table using the dbf library
    table = dbf.Table(dbf_file_path,
                      field_specs='name C(25); age N(3,0); birth D; qualified L',)
    table.open()

    records = []
    for record in table:
        try:
            # Convert the record to a dictionary and handle memo fields
            record_dict = {field: record[field] for field in table.field_names}
            records.append(record_dict)
        except Exception as e:
            print(f"Skipping a record due to an error: {e}")

    # Convert the list of records (dictionaries) to a pandas DataFrame
    df = pd.DataFrame(records)

    table.close()
    return df

# Usage
dbf_file_path = r'D:\PycharmProjects\django-odbc\Logis\DANE\bok.DBF'
df = dbf_to_df(dbf_file_path)
print(df)
