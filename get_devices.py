import os
import django

import pandas as pd


pd.set_option("display.max_columns", None)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logis_orm.settings')

# Initiate Django for standalone scripts
django.setup()
from dbf_operations.models import Ksiazka_k, Indexy_4
from tools import JSONOperations

class Main:
    """
    Main class for processing data from Ksiazka_k and Indexy_4 models.

    Attributes
    ----------
    selected_ksiazka_k_columns : list of str
        Selected columns from Ksiazka_k model.
    indexy4_selected_columns : list of str
        Selected columns from Indexy_4 model.
    final_column_order : list of str
        Final order of columns in the processed DataFrame.

    Methods
    -------
    process()
        Process the data and saves it as a JSON file.
    _process_ksiazka_k()
        Process the Ksiazka_k data and return the processed DataFrame.
    _process_indexy_4()
        Process the Indexy_4 data and store the processed DataFrame in 'indexy4' attribute.
    _filter_sort_and_rearrange_df()
        Filter, sort, and rearrange the DataFrame.
    _merge_df_with_indexy4()
        Merge the DataFrame with the 'indexy4' attribute based on common indices.
    _drop_unnecessary_columns()
        Drop unnecessary columns from the DataFrame.
    _rename_columns()
        Rename columns of the DataFrame.
    _format_and_reorder_df()
        Format and reorder columns of the DataFrame.
    """
    selected_ksiazka_k_columns = [
        'k_pr_sp_nr', 'p_ind_rek', 'indeks', 'u_data_p',
        'k_do_pesel', 'k_do_nazw', 'p_typ', 'p_nr_fab',
        'u_nazwa_s', 'k_do_datap', 'k_data_sp'
    ]

    indexy4_selected_columns = [
        'indeks', 'nazwa', 'p_pwaz_k', 'p_pwaz_u', 'p_norma_k', 'p_norma_u'
    ]

    final_column_order = [
        'indeks_rekordu', 'ium', 'nazwa', 'typ', 'nr_fabryczny', 'data_przyjecia',
        'dni_w_BOK', 'data_pobrania', 'nr_ksiazka_k', 'uzytkownik',
        'rbh_kontrolny', 'rbh_uzytkowy', 'pesel', 'kalibrujacy'
    ]

    def __init__(self):
        self.df = None
        self.indexy4 = None

    def process(self):
        self.df = self._process_ksiazka_k()
        self._process_indexy_4()
        self._filter_sort_and_rearrange_df()
        self._merge_df_with_indexy4()
        self._drop_unnecessary_columns()
        self._rename_columns()
        self._format_and_reorder_df()
        JSONOperations.save(self.df, 'devices_list.json')
        devices_loaded = JSONOperations.load('devices_list.json')
        print(devices_loaded)
        return self.df

    def _process_ksiazka_k(self):
        df = Ksiazka_k.objects.to_pd()[self.selected_ksiazka_k_columns]
        df['indeks8'] = df['indeks'].str[:8]
        df['ium'] = df['indeks'].str[:6]

        df['u_data_p'] = pd.to_datetime(df['u_data_p']).dt.date
        df['k_do_datap'] = pd.to_datetime(df['k_do_datap']).dt.date
        df['k_data_sp'] = pd.to_datetime(df['k_data_sp']).dt.date

        df['dni_w_BOK'] = (pd.to_datetime("now").date() - df['u_data_p']).dt.days

        return df

    def _process_indexy_4(self):
        self.indexy4 = Indexy_4.objects.to_pd()[self.indexy4_selected_columns]
        self.indexy4['indeks8'] = self.indexy4['indeks'].str[:8]

    def _filter_sort_and_rearrange_df(self):
        self.df = self.df[
            self.df['k_data_sp'].apply(lambda x: x.year) < 1900]  # Skip instruments that have been calibrated
        self.df = self.df.sort_values(by='dni_w_BOK', ascending=False)

        cols = list(self.df.columns)
        cols.remove('dni_w_BOK')
        cols = ['dni_w_BOK'] + cols
        self.df = self.df[cols]

    def _merge_df_with_indexy4(self):
        indexy4_filtered8 = self.indexy4[self.indexy4['indeks'].str.len() == 8]
        merged_df = self.df.merge(indexy4_filtered8[['indeks8', 'nazwa']], on='indeks8', how='left')
        self.df = merged_df.merge(self.indexy4[['indeks', 'p_norma_k', 'p_norma_u']], on='indeks', how='left')

    def _drop_unnecessary_columns(self):
        self.df = self.df.drop(columns=['indeks', 'indeks8', 'k_data_sp'])

    def _rename_columns(self):
        self.df = self.df.rename(columns={
            'k_pr_sp_nr': 'nr_ksiazka_k',
            'p_ind_rek': 'indeks_rekordu',
            'u_data_p': 'data_przyjecia',
            'k_do_pesel': 'pesel',
            'k_do_datap': 'data_pobrania',
            'k_do_nazw': 'kalibrujacy',
            'p_typ': 'typ',
            'p_nr_fab': 'nr_fabryczny',
            'u_nazwa_s': 'uzytkownik',
            'p_norma_k': 'rbh_kontrolny',
            'p_norma_u': 'rbh_uzytkowy'
        })

    def _format_and_reorder_df(self):
        self.df['data_przyjecia'] = self.df['data_przyjecia'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
        self.df['data_pobrania'] = self.df['data_pobrania'].apply(
            lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
        self.df = self.df[self.final_column_order]

def get_devices():
    """
    Retrieve a list of devices.

    :return: A list of devices.
    """
    return Main().process()

if __name__ == '__main__':
    get_devices()
