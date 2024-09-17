import pandas as pd
pd.set_option("display.max_columns", None)
import numpy as np
from tools.settings import INDEX_PRACOWNI
from tools.ODBCDataLoader import DataLoader

class DevicesDataProcessor:
    """
    This class is used to process device data. It loads the initial dataframe, filters it,
    adds necessary columns, and performs data merges.
    """

    def __init__(self):
        self.columns_to_use_in_ksiazka_k=['pr_id','p_nr_fab','p_typ','u_nazwa_s','k_do_k_n','k_do_data','k_do_nazw','k_do_datap','k_bk_data','k_data_sp']
        self.data_loader = DataLoader()
        self.indexy_4 = self.data_loader.indexy_4
        self.ind4_om = self.data_loader.ind4_om[['indeks', 'p_norma_k']]
        self.ksiazka_k = self.data_loader.ksiazka_k
        print(self.ksiazka_k.head())

    def filter_bok_by_pracownia(self, selected_columns):
        """
        Filters the ksiazka_k dataframe (referred as BOK) by a specific ID (INDEX_PRACOWNI) and two date conditions.
        Only includes the selected columns in the returned dataframe.
        """
        bok = self.ksiazka_k[selected_columns]
        return bok[
            (bok['pr_id'] == INDEX_PRACOWNI) &
            (bok['k_do_data'] > '1900-01-01') &
            (bok['k_do_datap'] < '1900-01-01')
            ].copy()

    def add_ium_and_indeks8_columns(self, bok, columns):
        """
        Adds two new columns 'ium' and 'indeks8' to the dataframe.
        These columns are derived from the 'indeks' column by taking substrings of the 'indeks' entries.
        """
        bok['ium'] = bok['indeks'].str[:6]
        columns.insert(columns.index('indeks') + 1, 'ium')
        bok_with_ium = bok[columns].copy()
        bok_with_ium['indeks8'] = bok_with_ium['indeks'].str[:8]
        return bok_with_ium

    def prepare_reduced_bok(self):
        """
        Obtains the reduced BOK dataframe by first filtering the initial dataframe
        and then adding the necessary 'ium' and 'indeks8' columns to it.
        """
        selected_columns = [
            'pr_id', 'p_nr_fab', 'u_nazwa_s', 'u_data_p', 'k_do_data',
            'k_do_pesel', 'k_do_datap', 'k_bk_data', 'p_ind_rek',
            'p_typ', 'indeks'
        ]
        reduced_columns = [
            'p_ind_rek', 'indeks', 'p_typ', 'p_nr_fab',
            'u_data_p', 'k_do_pesel', 'u_nazwa_s'
        ]
        filtered_bok = self.filter_bok_by_pracownia(selected_columns)
        return self.add_ium_and_indeks8_columns(filtered_bok, reduced_columns)

    def update_indexy_rbh(self, indexy_rbh):
        """
        Updates the 'indexy_rbh' dataframe using the 'ind4_om' dataframe.
        The updates are performed based on the 'indeks' column.
        """
        self.ind4_om.set_index('indeks', inplace=True)
        indexy_rbh.update(self.ind4_om)
        indexy_rbh.reset_index(inplace=True)
        return indexy_rbh

    def merge_with_indexy_rbh(self, bok):
        """
        Merges the BOK dataframe with 'indexy_rbh' dataframe on the 'indeks' column.
        'indexy_rbh' is the dataframe that contains updated data from the 'ind4_om' dataframe.
        """
        indexy_rbh = self.indexy_4[self.indexy_4['indeks'].str.len() == 11][['indeks', 'p_norma_k']]
        indexy_rbh.set_index('indeks', inplace=True)
        indexy_rbh = self.update_indexy_rbh(indexy_rbh)
        return pd.merge(bok, indexy_rbh, how='left', on='indeks')

    def merge_with_indexy_names(self, bok):
        """
        Merges the BOK dataframe with 'indexy_names' dataframe on the 'indeks8' column,
        which results in a new dataframe with the name column added.
        """
        indexy_names = self.indexy_4[self.indexy_4['indeks'].str.len() == 8][['indeks', 'nazwa']]
        return pd.merge(
            bok, indexy_names, how='left',
            left_on='indeks8', right_on='indeks', suffixes=('', '_y')
        ).drop(columns=['indeks_y'])

    def get_devices_waiting_for_calibration(self):
        """
        Returns a dataframe of devices waiting for calibration.
        This is achieved by preparing the BOK dataframe, merging it with the 'indexy_rbh' dataframe,
        merging the resultant dataframe with the 'indexy_names' dataframe and selecting specific final columns.
        """
        reduced_bok = self.prepare_reduced_bok()
        reduced_bok = self.merge_with_indexy_rbh(reduced_bok)
        reduced_bok = self.merge_with_indexy_names(reduced_bok)
        final_columns = [
            'p_ind_rek', 'ium', 'nazwa', 'p_typ', 'p_nr_fab',
            'p_norma_k', 'u_data_p', 'u_nazwa_s', 'k_do_pesel'
        ]
        return reduced_bok[final_columns]

    @staticmethod
    def initialize():
        """
        Initializes and processes data to return three key dataframes used in the workflow:
        uncalibrated_devices_in_bok - dataframe of devices waiting for calibration,
        rbh_for_pesel - summarised dataframe with summed 'p_norma_k' for each unique 'k_do_pesel',
        devices_in_bok_to_select - dataframe of devices in BOK that need to be selected.
        """
        processor = DevicesDataProcessor()
        uncalibrated_devices_in_bok = processor.get_devices_waiting_for_calibration()

        rbh_for_pesel = uncalibrated_devices_in_bok.groupby('k_do_pesel')['p_norma_k'].sum().reset_index()
        rbh_for_pesel = rbh_for_pesel.sort_values(by='p_norma_k').rename(columns={'p_norma_k': 'selected_rbh'})

        devices_in_bok_to_select = uncalibrated_devices_in_bok[uncalibrated_devices_in_bok['k_do_pesel'].isna()]

        return uncalibrated_devices_in_bok, rbh_for_pesel, devices_in_bok_to_select


# Initialize data
#uncalibrated_devices_in_bok, rbh_for_pesel, devices_in_bok_to_select = DevicesDataProcessor.initialize()

if __name__ == '__main__':
    #print(f'\nUncalibrated Devices in BOK:\n{uncalibrated_devices_in_bok}')
    #print(f'\nRBH for PESEL:\n{rbh_for_pesel}')
    #print(f'\nDevices in BOK to Select:\n{devices_in_bok_to_select}')

    columns_to_use_in_ksiazka_k = ['bk_id', 'pr_id', 'p_nr_fab', 'p_typ', 'u_nazwa_s', 'k_do_k_n', 'k_do_nazw', 'k_do_datap', 'k_uwagi', 'indeks',
                                #   'k_bk_data', 'k_data_sp', 'k_do_data'
                                   ]

    data_loader = DataLoader()
    indexy_4 = data_loader.indexy_4
    ind4_om = data_loader.ind4_om[['indeks', 'p_norma_k']]

    bok = data_loader.bok[['bk_id', 'u_data_p']]
    ksiazka_k = data_loader.ksiazka_k[columns_to_use_in_ksiazka_k]

    # Dopasowanie danych z 'bok' do 'ksiazka_k' na podstawie 'bk_id' w celu dodania daty przyjęcia do BOK
    ksiazka_k = pd.merge(ksiazka_k, bok, on='bk_id', how='left')
    ksiazka_k['ium'] = ksiazka_k['indeks'].str[:6]
    ksiazka_k['indeks_8'] = ksiazka_k['indeks'].str[:8]  # need for name


####################################################################
    # Aktualizacja tabeli 'indexy_4' za pomocą danych z 'ind4_om'
    ind4_om.set_index('indeks', inplace=True)  # Ustaw indeks na kolumnę 'indeks'
    indexy_4.set_index('indeks', inplace=True)  # Ustaw indeks na kolumnę 'indeks'

    # Aktualizacja tabeli 'indexy_4' na podstawie danych z 'ind4_om'
    indexy_4.update(ind4_om)

    # Przywrócenie indeksów do domyślnej postaci
    indexy_4.reset_index(inplace=True)
    ind4_om.reset_index(inplace=True)

    # Wyświetlenie zaktualizowanej tabeli 'indexy_4'
    print(f'\nZaktualizowana tabela indexy_4:\n{indexy_4.head()}')
#################################################################
#    wybierz tylko przyrządy do kalibracji w bok

    ksiazka_k=ksiazka_k[
        (ksiazka_k['k_do_k_n'] == 2)   # tylko przyrządy do kalibracji
        & (ksiazka_k['pr_id'] == INDEX_PRACOWNI)
        #(ksiazka_k['k_do_data'] > '1900-01-01') &
        #& (ksiazka_k['k_do_datap'] < '1900-01-01')
        & (ksiazka_k['k_do_datap'].isnull())
        ]



################################################

    ksiazka_k = pd.merge(ksiazka_k, indexy_4[['indeks','nazwa']], left_on='indeks_8', right_on='indeks', how='left', suffixes=('', '_drop'))

    # Usunięcie dodatkowej kolumny 'indeks', jeśli nie jest potrzebna
    ksiazka_k = ksiazka_k.drop(columns=['indeks_drop'])

    ksiazka_k = pd.merge(ksiazka_k, indexy_4[['indeks','p_norma_k']],on='indeks', how='left')


    column_name='pr_id' #'k_do_datap' 'pr_id'
    # Zliczanie wartości i sortowanie rosnąco
    sorted_value_counts = ksiazka_k[column_name].value_counts().sort_values(ascending=True)

    # Wyświetlanie całej tabeli
    print(sorted_value_counts)

    # Wyświetlanie minimalnej i maksymalnej wartości
    print(f"Min: {ksiazka_k[column_name].min()}")
    print(f"Max: {ksiazka_k[column_name].max()}")

    # Dodanie kolumny 'dni_w_om', która wylicza liczbę dni między dzisiejszą datą a 'u_data_p'
    today = pd.Timestamp('today').normalize()  # Pobieranie dzisiejszej daty bez godziny
    ksiazka_k['u_data_p'] = pd.to_datetime(ksiazka_k['u_data_p'])  # Konwersja kolumny 'u_data_p' na typ daty
    ksiazka_k['dni_w_om'] = (today - ksiazka_k['u_data_p']).dt.days  # Wyliczanie różnicy w dniach

    columns_to_drop=['u_data_p','bk_id','pr_id','k_do_k_n','k_do_datap','indeks','indeks_8']
    ksiazka_k=ksiazka_k.drop(columns=columns_to_drop)
    columns_order=['ium','dni_w_om','nazwa','p_typ','p_nr_fab','k_uwagi','u_nazwa_s','k_do_nazw','p_norma_k']

    ksiazka_k = ksiazka_k[columns_order]

    print(ksiazka_k.head())
    print(ksiazka_k.info())