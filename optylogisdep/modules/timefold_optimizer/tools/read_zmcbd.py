import pandas as pd
from dbfread import DBF
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader

# Odczyt danych za pomocą dbfread
file_path = r'G:\PycharmProject\Timefold-training\Logis\DANE\przyrzad_zmcbd.DBF'
table = DBF(file_path)
print(dir(table))


df_dbfread = pd.DataFrame(iter(table))

# Odczyt danych za pomocą ODBC (używając DataLoader)
data_loader = DataLoader(remove_csv_after_read=True)
df_odbc = data_loader.przyrzad_zmcbd

# Porównanie liczby wierszy
print("Liczba wierszy (dbfread):", len(df_dbfread))
print("Liczba wierszy (ODBC):", len(df_odbc))

# Znalezienie różnic
difference = pd.concat([df_dbfread, df_odbc]).drop_duplicates(keep=False)
print("Różnice między zestawami danych:")
print(difference)
