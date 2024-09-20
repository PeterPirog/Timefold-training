import pandas as pd
import numpy as np
import os
import ast  # Import dla funkcji literal_eval do konwersji stringów na listy
from tools.settings import INDEX_PRACOWNI, EXCLUDED_WORDS_LIST
from tools.ODBCDataLoader import DataLoader

pd.set_option("display.max_columns", None)

class DevicesDataProcessor:
    """
    This class processes device data, including filtering, adding columns, and performing merges.
    """

    def __init__(self):
        self.columns_to_use_in_ksiazka_k = ['bk_id', 'pr_id', 'p_nr_fab', 'p_typ', 'u_nazwa_s', 'k_do_k_n', 'k_do_nazw', 'k_do_datap', 'k_uwagi', 'indeks']
        self.data_loader = DataLoader()
        self.indexy_4 = self.data_loader.indexy_4
        self.ind4_om = self.data_loader.ind4_om[['indeks', 'p_norma_k']]
        self.ksiazka_k = self.data_loader.ksiazka_k
        self.bok = self.data_loader.bok[['bk_id', 'u_data_p']]

    def update_indexy_rbh(self):
        """
        Updates the 'indexy_4' dataframe using the 'ind4_om' dataframe based on 'indeks' column.
        """
        self.ind4_om.set_index('indeks', inplace=True)
        self.indexy_4.set_index('indeks', inplace=True)
        self.indexy_4.update(self.ind4_om)
        self.indexy_4.reset_index(inplace=True)
        self.ind4_om.reset_index(inplace=True)

    def prepare_ksiazka_k(self):
        """
        Prepares 'ksiazka_k' dataframe by merging it with 'bok' and 'indexy_4', filtering by calibration devices, and adding necessary columns.
        """
        ksiazka_k = pd.merge(self.ksiazka_k[self.columns_to_use_in_ksiazka_k], self.bok, on='bk_id', how='left')
        ksiazka_k['ium'] = ksiazka_k['indeks'].str[:6]
        ksiazka_k['indeks_8'] = ksiazka_k['indeks'].str[:8]

        # Filter for devices for calibration in the specified lab
        ksiazka_k = ksiazka_k[(ksiazka_k['k_do_k_n'] == 2) & (ksiazka_k['pr_id'] == INDEX_PRACOWNI) & (ksiazka_k['k_do_datap'].isnull())]

        # Merge with 'indexy_4' for additional data
        ksiazka_k = pd.merge(ksiazka_k, self.indexy_4[['indeks', 'nazwa']], left_on='indeks_8', right_on='indeks', how='left', suffixes=('', '_drop'))
        ksiazka_k = ksiazka_k.drop(columns=['indeks_drop'])
        ksiazka_k = pd.merge(ksiazka_k, self.indexy_4[['indeks', 'p_norma_k']], on='indeks', how='left')

        # Add 'dni_w_om' column (days in BOK)
        today = pd.Timestamp('today').normalize()
        ksiazka_k['u_data_p'] = pd.to_datetime(ksiazka_k['u_data_p'])
        ksiazka_k['dni_w_om'] = (today - ksiazka_k['u_data_p']).dt.days

        # Drop unnecessary columns and reorder the dataframe
        columns_to_drop = ['u_data_p', 'bk_id', 'pr_id', 'k_do_k_n', 'k_do_datap', 'indeks', 'indeks_8']
        ksiazka_k = ksiazka_k.drop(columns=columns_to_drop)
        columns_order = ['ium', 'dni_w_om', 'nazwa', 'p_typ', 'p_nr_fab', 'k_uwagi', 'u_nazwa_s', 'k_do_nazw', 'p_norma_k']
        return ksiazka_k[columns_order]

    def get_devices_in_bok_to_assign(self, ksiazka_k):
        """
        Filters devices in BOK to assign based on missing 'k_do_nazw' and excludes rows with certain words in 'k_uwagi'.
        """
        devices_in_bok_to_assign = ksiazka_k[ksiazka_k['k_do_nazw'].isnull() | (ksiazka_k['k_do_nazw'] == '')]
        for word in EXCLUDED_WORDS_LIST:
            devices_in_bok_to_assign = devices_in_bok_to_assign[~devices_in_bok_to_assign['k_uwagi'].str.contains(word, case=False, na=False)]
        return devices_in_bok_to_assign

    def get_rbh_for_technician(self, ksiazka_k):
        """
        Groups devices by 'k_do_nazw' and sums 'p_norma_k' for each unique 'k_do_nazw' (technician).
        """
        rbh_for_pesel = ksiazka_k.groupby('k_do_nazw', as_index=False)['p_norma_k'].sum()
        rbh_for_pesel = rbh_for_pesel.rename(columns={'p_norma_k': 'sum_p_norma_k'})
        return rbh_for_pesel.sort_values(by='k_do_nazw', ascending=True)

    @staticmethod
    def initialize():
        """
        Initializes and returns uncalibrated devices, RBH for technicians, and devices to assign.
        """
        processor = DevicesDataProcessor()
        processor.update_indexy_rbh()
        uncalibrated_devices_in_bok = processor.prepare_ksiazka_k()
        rbh_for_pesel = processor.get_rbh_for_technician(uncalibrated_devices_in_bok)
        devices_in_bok_to_assign = processor.get_devices_in_bok_to_assign(uncalibrated_devices_in_bok)
        return uncalibrated_devices_in_bok, rbh_for_pesel, devices_in_bok_to_assign


class TechnicianDataProcessor:
    """
    This class processes technician data including merging, filtering, grouping, and sorting.
    """

    def __init__(self):
        self.data_loader = DataLoader(INDEX_PRACOWNI)
        self.pers_gr = self.data_loader.pers_gr
        self.pers_st = self.data_loader.pers_st

    def merge_personal_data(self) -> pd.DataFrame:
        """
        Merges the personal group dataframe and the state dataframe based on 'l_pesel' (ID).
        """
        return pd.merge(self.pers_gr, self.pers_st, how='left', left_on='l_pesel', right_on='l_pesel')

    def filter_technicians(self, merged_data: pd.DataFrame) -> pd.DataFrame:
        """
        Filters merged data for technicians with the right status and ID.
        """
        return merged_data[(merged_data['pr_id'] == INDEX_PRACOWNI) & (merged_data['ium'].notna()) & (~merged_data['zaw']) & (~merged_data['cof']) & (merged_data['l_status_p'] == 2)]

    def group_technicians(self, filtered_data: pd.DataFrame) -> pd.DataFrame:
        """
        Groups technicians by relevant details and aggregates 'ium' data into lists, sorted alphabetically.
        """
        grouped_df = filtered_data.groupby(['l_pesel', 'l_nazw_im', 'l_pr_thn', 'pr_id', 'l_norma_p']).agg(
            iums=('ium', lambda x: sorted(list(x.dropna())))).reset_index()

        self.format_technician_columns(grouped_df)
        return grouped_df

    def format_technician_columns(self, df: pd.DataFrame) -> None:
        """
        Formats 'l_nazw_im', calculates 'rbh_week_plan', and removes unnecessary columns.
        """
        df['l_nazw_im'] = df['l_nazw_im'].str.strip()
        df['rbh_week_plan'] = (df['l_pr_thn'] * df['l_norma_p'] / 1400).apply(np.floor)
        df.drop(columns=['l_pr_thn', 'l_norma_p'], inplace=True)
        df = df[['l_nazw_im', 'rbh_week_plan', 'iums']]

    def sort_technicians(self, grouped_data: pd.DataFrame) -> pd.DataFrame:
        """
        Sorts technicians by name and removes unnecessary columns.
        """
        grouped_data = grouped_data.drop(['pr_id', 'l_pesel'], axis=1)
        return grouped_data.sort_values(by='l_nazw_im')

    def process_technician_data(self) -> pd.DataFrame:
        """
        Processes technician data through merging, filtering, grouping, and sorting.
        """
        merged_data = self.merge_personal_data()
        filtered_data = self.filter_technicians(merged_data)
        grouped_data = self.group_technicians(filtered_data)

        # Ensure the 'iums' are always sorted after processing.
        grouped_data['iums'] = grouped_data['iums'].apply(sorted)

        return self.sort_technicians(grouped_data)

    @staticmethod
    def initialize():
        """
        Initializes and processes technician data to return the final dataframe.
        """
        processor = TechnicianDataProcessor()
        return processor.process_technician_data()

def get_technician_and_device_data(use_archive_data=False):
    """
    Initializes and returns both technicians and devices in BOK to assign.
    Uses archived CSV data if 'use_archive_data' is set to True.
    """
    csv_dir = 'CSV_files'
    technicians_csv_path = os.path.join(csv_dir, 'technicians.csv')
    devices_csv_path = os.path.join(csv_dir, 'devices_in_bok_to_assign.csv')

    if use_archive_data and os.path.exists(technicians_csv_path) and os.path.exists(devices_csv_path):
        # Load archived data
        technicians = pd.read_csv(technicians_csv_path)
        devices_in_bok_to_assign = pd.read_csv(devices_csv_path)

        # Convert 'iums' column back to list format and sort them
        technicians['iums'] = technicians['iums'].apply(ast.literal_eval).apply(sorted)
    else:
        # Get uncalibrated devices, RBH for technicians, and devices to assign
        uncalibrated_devices_in_bok, assigned_rbh_for_technician, devices_in_bok_to_assign = DevicesDataProcessor.initialize()

        # Initialize technicians
        technicians = TechnicianDataProcessor.initialize()

        # Merge technicians with RBH data
        technicians = pd.merge(technicians, assigned_rbh_for_technician, how='left', left_on='l_nazw_im', right_on='k_do_nazw')
        technicians['sum_p_norma_k'] = technicians['sum_p_norma_k'].fillna(0)

        # Reorganize columns and clean up
        technicians = technicians.drop('k_do_nazw', axis=1)
        iums_column = technicians.pop('iums')
        technicians['iums'] = iums_column.apply(sorted)  # Sort 'iums' alphabetically
        technicians = technicians.rename(columns={'l_nazw_im': 'technician', 'rbh_week_plan': 'rbh_do_zaplanowania', 'sum_p_norma_k': 'rbh_przydzielone'})

        # if all rbh are assigned 'rbh_do_zaplanowania' =0
        technicians['rbh_do_zaplanowania'] = (technicians['rbh_do_zaplanowania'] - technicians['rbh_przydzielone']).clip(lower=0)

        # Rename and sort devices to assign
        devices_in_bok_to_assign = devices_in_bok_to_assign.rename(columns={'p_typ': 'typ', 'p_nr_fab': 'nr_fabryczny', 'u_nazwa_s': 'uzytkownik', 'k_do_nazw': 'technician', 'p_norma_k': 'rbh_norma'})
        devices_in_bok_to_assign = devices_in_bok_to_assign.drop('k_uwagi', axis=1).sort_values(by='dni_w_om', ascending=False)

        # Save data to CSV for future use
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        technicians.to_csv(technicians_csv_path, index=False)
        devices_in_bok_to_assign.to_csv(devices_csv_path, index=False)

    return technicians, devices_in_bok_to_assign


if __name__ == '__main__':
    # Change to True to use archived data for faster testing
    technicians, devices_in_bok_to_assign = get_technician_and_device_data(use_archive_data=False)

    # Display results
    print(f'\nTechnicians:\n{technicians.head()}')
    print(f'\nDevices in BOK to Assign:\n{devices_in_bok_to_assign.head()}')
