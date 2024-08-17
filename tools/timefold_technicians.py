import pandas as pd
import numpy as np

from tools.ODBCDataLoader import DataLoader
from tools.settings import INDEX_PRACOWNI
from dataclasses import dataclass
from typing import Annotated, Set, List
from timefold.solver.domain import PlanningId


@dataclass
class Technician:
    """
    A class representing a Technician.

    Attributes:
        id: An annotated integer representing the unique id of a technician.
        pesel: A string representing the PESEL number of a technician.
        name: A string representing the name of a technician.
        rbh_week_plan: A float representing the weekly work plan hours of a technician.
        iums: A set of strings representing the ium values of a technician.
    """
    id: Annotated[int, PlanningId]
    pesel: str
    name: str
    rbh_week_plan: float
    iums: Set[str]

    def has_ium(self, ium: str) -> bool:
        """Checks if the given ium is in the technician's iums."""
        return ium in self.iums

    def __str__(self) -> str:
        """Returns a string representation of the technician."""
        return f"Technician(id={self.id}, name={self.name}, pesel={self.pesel}, rbh_week_plan={self.rbh_week_plan}, iums={self.iums})"


class TechnicianDataProcessor:
    """
    A class to process data related to technicians.

    Attributes:
        pers_gr: A DataFrame containing the personal group data.
        pers_st: A DataFrame containing the personal state data.
    """

    def __init__(self, pers_gr: pd.DataFrame, pers_st: pd.DataFrame):
        self.pers_gr = pers_gr
        self.pers_st = pers_st

    def process_technician_data(self) -> pd.DataFrame:
        """
        Processes the data related to technicians by merging, filtering, grouping, and sorting it.
        Returns the final sorted and processed DataFrame.
        """
        merged_data = self._merge_technician_dataframes()
        filtered_data = self._filter_technician_data(merged_data)
        grouped_data = self._group_by_technician_details(filtered_data)
        final_sorted_data = self._sort_technician_data(grouped_data)
        return final_sorted_data

    def _merge_technician_dataframes(self) -> pd.DataFrame:
        """Merges the personal group and state dataframes based on the 'l_pesel' column. Returns the merged DataFrame."""
        return pd.merge(self.pers_gr, self.pers_st, how='left', left_on='l_pesel', right_on='l_pesel')

    def _filter_technician_data(self, result: pd.DataFrame) -> pd.DataFrame:
        """Filters the merged dataframe based on certain conditions. Returns the filtered DataFrame."""
        calibration_personnel_status = 2
        filtered_result = result[
            (result['pr_id'] == INDEX_PRACOWNI) &
            (result['ium'].notna()) &
            (~result['zaw']) &
            (~result['cof']) &
            (result['l_status_p'] == calibration_personnel_status)
            ]
        return filtered_result

    def _group_by_technician_details(self, filtered_result: pd.DataFrame) -> pd.DataFrame:
        """Groups the filtered dataframe by certain columns and refactors it. Returns the grouped DataFrame."""
        grouped_df = filtered_result.groupby(
            ['l_pesel', 'l_nazw_im', 'l_pr_thn', 'pr_id', 'l_norma_p']).agg(
            iums=('ium', lambda x: list(x.dropna())))
        grouped_df.reset_index(inplace=True)
        self._format_final_data_columns(grouped_df)
        return grouped_df

    def _format_final_data_columns(self, groups: pd.DataFrame) -> None:
        """Formats certain columns in the groups dataframe."""
        groups['l_nazw_im'] = groups['l_nazw_im'].str.strip()
        groups['rbh_week_plan'] = (groups['l_pr_thn'] * groups['l_norma_p'] / 1400).apply(np.floor)
        groups.loc[groups['rbh_week_plan'] == 40, 'rbh_week_plan'] = 48
        groups.loc[groups['rbh_week_plan'] < 24, 'rbh_week_plan'] = 24

    def _sort_technician_data(self, grouped_filtered_result: pd.DataFrame) -> pd.DataFrame:
        """Sorts the grouped and filtered dataframe by 'l_nazw_im' column and drops the 'pr_id' column. Returns the sorted DataFrame."""
        return grouped_filtered_result.sort_values(by='l_nazw_im').drop('pr_id', axis=1)


def generate_technician_datatables() -> List[Technician]:
    """
    Generates a list of Technician objects based on processed data.

    Returns:
        A list of Technician objects.
    """
    dl = DataLoader(remove_csv_after_read=False)
    dt_processor = TechnicianDataProcessor(dl.pers_gr, dl.pers_st)
    sorted_filtered_result = dt_processor.process_technician_data()
    return [_create_technician(index, row) for index, row in sorted_filtered_result.iterrows()]


def _create_technician(index: int, row: pd.Series) -> Technician:
    """
    Creates and returns a Technician object based on given row data.
    """
    return Technician(index, row['l_pesel'], row['l_nazw_im'], row['rbh_week_plan'], set(row['iums']))


if __name__ == '__main__':
    technicians = generate_technician_datatables()
    for technician in technicians:
        print(technician)
