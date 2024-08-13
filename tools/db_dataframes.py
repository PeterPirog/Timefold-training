import os
import pandas as pd
from tools.dbf_tools import dbf_to_df
from tools.settings import DATE_COLUM_LIST, dbf_paths

class Logis:
    def __init__(self):
        self._dataframes = {}

    def _load_df(self, key):
        """Internal method to load a DataFrame from a DBF file if not already loaded."""
        if key not in self._dataframes:
            print(f"Loading {key} from {dbf_paths[key]}...")
            self._dataframes[key] = dbf_to_df(dbf_file_path=dbf_paths[key], date_column_list=DATE_COLUM_LIST)
        return self._dataframes[key]

    @property
    def index_4(self):
        return self._load_df('index_4')

    @property
    def pers_gr(self):
        return self._load_df('pers_gr')

    @property
    def pers_st(self):
        return self._load_df('pers_st')

    @property
    def ksiazka_k(self):
        return self._load_df('ksiazka_k')

    @property
    def ksiazka_k_arch(self):
        return self._load_df('ksiazka_k_arch')

    @property
    def om_zu(self):
        return self._load_df('om_zu')

    @property
    def pdf_protspr(self):
        return self._load_df('pdf_protspr')

    @property
    def przyrzad_zmcbd(self):
        return self._load_df('przyrzad_zmcbd')

    @property
    def uzytkownik(self):
        return self._load_df('uzytkownik')

    @property
    def osrodek_met(self):
        return self._load_df('osrodek_met')

    @property
    def osrodek_pr(self):
        return self._load_df('osrodek_pr')

    @property
    def pyt_podstawa(self):
        return self._load_df('pyt_podstawa')

    @property
    def bok(self):
        return self._load_df('bok')

if __name__ == '__main__':
# Usage
    logis = Logis()

    # Accessing DataFrames, which will load the DBF file if not already loaded
    pers_gr_df = logis.pers_gr
    print(pers_gr_df)

    index_4_df = logis.index_4
    print(index_4_df)


"""

# Load DBF files into DataFrames
#bok = dbf_to_df(dbf_file_path=dbf_paths['bok'], date_column_list=DATE_COLUM_LIST)
#bok_arch = dbf_to_df(dbf_file_path=dbf_paths['bok_arch'], date_column_list=DATE_COLUM_LIST)
# problems with memo

index_4 = dbf_to_df(dbf_file_path=dbf_paths['index_4'], date_column_list=DATE_COLUM_LIST)
pers_gr = dbf_to_df(dbf_file_path=dbf_paths['pers_gr'], date_column_list=DATE_COLUM_LIST)
pers_st = dbf_to_df(dbf_file_path=dbf_paths['pers_st'], date_column_list=DATE_COLUM_LIST)
ksiazka_k = dbf_to_df(dbf_file_path=dbf_paths['ksiazka_k'], date_column_list=DATE_COLUM_LIST)
ksiazka_k_arch = dbf_to_df(dbf_file_path=dbf_paths['ksiazka_k_arch'], date_column_list=DATE_COLUM_LIST)
om_zu = dbf_to_df(dbf_file_path=dbf_paths['om_zu'], date_column_list=DATE_COLUM_LIST)
pdf_protspr = dbf_to_df(dbf_file_path=dbf_paths['pdf_protspr'], date_column_list=DATE_COLUM_LIST)
przyrzad_zmcbd = dbf_to_df(dbf_file_path=dbf_paths['przyrzad_zmcbd'], date_column_list=DATE_COLUM_LIST)
uzytkownik = dbf_to_df(dbf_file_path=dbf_paths['uzytkownik'], date_column_list=DATE_COLUM_LIST)
osrodek_met = dbf_to_df(dbf_file_path=dbf_paths['osrodek_met'], date_column_list=DATE_COLUM_LIST)
osrodek_pr = dbf_to_df(dbf_file_path=dbf_paths['osrodek_pr'], date_column_list=DATE_COLUM_LIST)
pyt_podstawa = dbf_to_df(dbf_file_path=dbf_paths['pyt_podstawa'], date_column_list=DATE_COLUM_LIST)

"""