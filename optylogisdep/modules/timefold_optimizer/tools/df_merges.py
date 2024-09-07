import pandas as pd
import numpy as np
from typing import List, Tuple
from optylogisdep.modules.timefold_optimizer.tools.settings import INDEX_PRACOWNI, EXCLUDED_WORDS_LIST
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader


class DevicesDataProcessor:
    """
    This class is used to process device data. It loads the initial dataframe, filters it,
    adds necessary columns, and performs data merges.
    """

    def __init__(self):
        self.data_loader: DataLoader = DataLoader()
        self.indexy_4: pd.DataFrame = self.data_loader.indexy_4
        self.ind4_om: pd.DataFrame = self.data_loader.ind4_om[['indeks', 'p_norma_k']]

    def filter_bok_by_pracownia(self, selected_columns: List[str]) -> pd.DataFrame:
        """
        Filters the BOK dataframe by a specific ID (INDEX_PRACOWNI) and two date conditions.
        Only includes the selected columns in the returned dataframe.
        """
        bok: pd.DataFrame = self.data_loader.bok[selected_columns]
        return bok[
            (bok['pr_id'] == INDEX_PRACOWNI) &
            (bok['k_do_data'] > '1900-01-01') &
            (bok['k_do_datap'] < '1900-01-01')
            ].copy()

    def add_ium_and_indeks8_columns(self, bok: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Adds two new columns 'ium' and 'indeks8' to the dataframe.
        These columns are derived from the 'indeks' column by taking substrings of the 'indeks' entries.
        """
        bok['ium'] = bok['indeks'].str[:6]
        columns.insert(columns.index('indeks') + 1, 'ium')
        bok_with_ium: pd.DataFrame = bok[columns].copy()
        bok_with_ium['indeks8'] = bok_with_ium['indeks'].str[:8]
        return bok_with_ium

    def prepare_reduced_bok(self) -> pd.DataFrame:
        """
        Obtains the reduced BOK dataframe by first filtering the initial dataframe
        and then adding the necessary 'ium' and 'indeks8' columns to it.
        """
        selected_columns: List[str] = [
            'pr_id', 'p_nr_fab', 'u_id', 'u_data_p', 'k_do_data',
            'k_do_pesel', 'k_do_datap', 'k_bk_data', 'p_ind_rek',
            'p_typ', 'u_nazwa_s', 'indeks'
        ]
        reduced_columns: List[str] = [
            'p_ind_rek', 'indeks', 'p_typ', 'p_nr_fab',
            'u_data_p', 'k_do_pesel', 'u_nazwa_s'
        ]
        filtered_bok: pd.DataFrame = self.filter_bok_by_pracownia(selected_columns)
        return self.add_ium_and_indeks8_columns(filtered_bok, reduced_columns)

    def update_indexy_rbh(self, indexy_rbh: pd.DataFrame) -> pd.DataFrame:
        """
        Updates the 'indexy_rbh' dataframe using the 'ind4_om' dataframe.
        The updates are performed based on the 'indeks' column.
        """
        self.ind4_om.set_index('indeks', inplace=True)
        indexy_rbh.update(self.ind4_om)
        indexy_rbh.reset_index(inplace=True)
        return indexy_rbh

    def merge_with_indexy_rbh(self, bok: pd.DataFrame) -> pd.DataFrame:
        """
        Merges the BOK dataframe with 'indexy_rbh' dataframe on the 'indeks' column.
        'indexy_rbh' is the dataframe that contains updated data from the 'ind4_om' dataframe.
        """
        indexy_rbh: pd.DataFrame = self.indexy_4[self.indexy_4['indeks'].str.len() == 11][['indeks', 'p_norma_k']]
        indexy_rbh.set_index('indeks', inplace=True)
        indexy_rbh = self.update_indexy_rbh(indexy_rbh)
        return pd.merge(bok, indexy_rbh, how='left', on='indeks')

    def merge_with_indexy_names(self, bok: pd.DataFrame) -> pd.DataFrame:
        """
        Merges the BOK dataframe with 'indexy_names' dataframe on the 'indeks8' column,
        which results in a new dataframe with the name column added.
        """
        indexy_names: pd.DataFrame = self.indexy_4[self.indexy_4['indeks'].str.len() == 8][['indeks', 'nazwa']]
        return pd.merge(
            bok, indexy_names, how='left',
            left_on='indeks8', right_on='indeks', suffixes=('', '_y')
        ).drop(columns=['indeks_y'])

    def get_devices_waiting_for_calibration(self) -> pd.DataFrame:
        """
        Returns a dataframe of devices waiting for calibration.
        This is achieved by preparing the BOK dataframe, merging it with the 'indexy_rbh' dataframe,
        merging the resultant dataframe with the 'indexy_names' dataframe and selecting specific final columns.
        """
        reduced_bok: pd.DataFrame = self.prepare_reduced_bok()
        reduced_bok = self.merge_with_indexy_rbh(reduced_bok)
        reduced_bok = self.merge_with_indexy_names(reduced_bok)
        final_columns: List[str] = [
            'p_ind_rek', 'ium', 'nazwa', 'p_typ', 'p_nr_fab',
            'p_norma_k', 'u_data_p', 'u_nazwa_s', 'k_do_pesel'
        ]
        return reduced_bok[final_columns]

    @staticmethod
    def initialize() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Initializes and processes data to return three key dataframes used in the workflow:
        uncalibrated_devices_in_bok - dataframe of devices waiting for calibration,
        rbh_for_pesel - summarised dataframe with summed 'p_norma_k' for each unique 'k_do_pesel',
        devices_in_bok_to_select - dataframe of devices in BOK that need to be selected.
        """
        processor = DevicesDataProcessor()
        uncalibrated_devices_in_bok: pd.DataFrame = processor.get_devices_waiting_for_calibration()

        rbh_for_pesel: pd.DataFrame = uncalibrated_devices_in_bok.groupby('k_do_pesel')['p_norma_k'].sum().reset_index()
        rbh_for_pesel = rbh_for_pesel.sort_values(by='p_norma_k').rename(columns={'p_norma_k': 'selected_rbh'})

        devices_in_bok_to_select: pd.DataFrame = uncalibrated_devices_in_bok[
            uncalibrated_devices_in_bok['k_do_pesel'].isna()]

        return uncalibrated_devices_in_bok, rbh_for_pesel, devices_in_bok_to_select


class TechnicianDataProcessor:
    """
    This class is used to process technician data. It loads the initial dataframe,
    merges it with another dataframe, filters, groups, and sorts the resultant dataframe.
    """

    def __init__(self):
        self.data_loader: DataLoader = DataLoader(INDEX_PRACOWNI)
        self.pers_gr: pd.DataFrame = self.data_loader.pers_gr
        self.pers_st: pd.DataFrame = self.data_loader.pers_st

    def merge_personal_data(self) -> pd.DataFrame:
        """
        Merges the personal group dataframe and the state dataframe,
        based on the 'l_pesel' column, which represents unique ID for each person in the dataframes.
        """
        return pd.merge(self.pers_gr, self.pers_st, how='left', left_on='l_pesel', right_on='l_pesel')

    def filter_technicians(self, merged_data: pd.DataFrame) -> pd.DataFrame:
        """
        Filters the merged dataframe based on specific conditions to get only the relevant technicians.
        The conditions include checking the ID (INDEX_PRACOWNI), null check on 'ium',
        and status checks on 'zaw', 'cof' and 'l_status_p'.
        """
        calibration_personnel_status: int = 2
        return merged_data[
            (merged_data['pr_id'] == INDEX_PRACOWNI) &
            (merged_data['ium'].notna()) &
            (~merged_data['zaw']) &
            (~merged_data['cof']) &
            (merged_data['l_status_p'] == calibration_personnel_status)
            ]

    def group_technicians(self, filtered_data: pd.DataFrame) -> pd.DataFrame:
        """
        Groups the filtered dataframe by technician details into a single dataframe
        and performs some aggregations on the grouped data.
        """
        grouped_df: pd.DataFrame = filtered_data.groupby(
            ['l_pesel', 'l_nazw_im', 'l_pr_thn', 'pr_id', 'l_norma_p']
        ).agg(
            iums=('ium', lambda x: list(x.dropna()))
        ).reset_index()
        self.format_technician_columns(grouped_df)
        return grouped_df

    def format_technician_columns(self, df: pd.DataFrame) -> None:
        """
        Formats the 'l_nazw_im' column by stripping whitespaces from the name, and adds a new 'rbh_week_plan' column.
        'rbh_week_plan' is derived from the 'l_pr_thn' and 'l_norma_p' columns, and adjusted based on specific conditions.
        """
        df['l_nazw_im'] = df['l_nazw_im'].str.strip()
        df['rbh_week_plan'] = (df['l_pr_thn'] * df['l_norma_p'] / 1400).apply(np.floor)
        df.loc[df['rbh_week_plan'] == 40, 'rbh_week_plan'] = 48
        df.loc[df['rbh_week_plan'] < 24, 'rbh_week_plan'] = 24

    def sort_technicians(self, grouped_data: pd.DataFrame) -> pd.DataFrame:
        """
        Sorts the grouped and filtered dataframe by technician name
        and drops the 'pr_id' column as it's not needed in the final dataframe.
        """
        return grouped_data.sort_values(by='l_nazw_im').drop('pr_id', axis=1)

    def process_technician_data(self) -> pd.DataFrame:
        """
        Processes the technician data by merging, filtering, grouping, and sorting.
        Returns the final processed dataframe which is ready for the next stages of the workflow.
        """
        merged_data: pd.DataFrame = self.merge_personal_data()
        filtered_data: pd.DataFrame = self.filter_technicians(merged_data)
        grouped_data: pd.DataFrame = self.group_technicians(filtered_data)
        return self.sort_technicians(grouped_data)

    @staticmethod
    def initialize() -> pd.DataFrame:
        """
        Initializes and processes technician data to return the final sorted dataframe.
        """
        processor = TechnicianDataProcessor()
        return processor.process_technician_data()


# Initialize data
uncalibrated_devices_in_bok, rbh_for_pesel, devices_in_bok_to_select = DevicesDataProcessor.initialize()
technicians = TechnicianDataProcessor.initialize()

# Further processing for technicians
technicians = pd.merge(technicians, rbh_for_pesel, how='left', left_on='l_pesel', right_on='k_do_pesel')
technicians['selected_rbh'] = technicians['selected_rbh'].fillna(0)
technicians = technicians.drop('k_do_pesel', axis=1)

technicians['free_rbh'] = technicians['rbh_week_plan'] - technicians['selected_rbh']
technicians['free_rbh'] = technicians['free_rbh'].apply(lambda x: max(x, 0))

# Move 'iums' column to the end
iums_column = technicians.pop('iums')
technicians['iums'] = iums_column

if __name__ == '__main__':
    print(f'\nUncalibrated Devices in BOK:\n{uncalibrated_devices_in_bok}')
    print(f'\nRBH for PESEL:\n{rbh_for_pesel}')
    print(f'\nDevices in BOK to Select:\n{devices_in_bok_to_select}')
    print(f'\nTechnicians:\n{technicians}')
