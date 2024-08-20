from typing import Dict
from datetime import datetime
from pandas import DataFrame
import pandas as pd
#from ..tools.df_merges import technicians, devices_in_bok_to_select


import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, '..'))

from timefold_optimizer.tools.df_merges import technicians, devices_in_bok_to_select

from dataclasses import dataclass, field
from typing import Annotated, Set, List, Union
from timefold.solver.domain import PlanningId, planning_entity, PlanningVariable
from timefold.solver.domain import planning_solution, PlanningEntityCollectionProperty, ProblemFactCollectionProperty, ValueRangeProvider, PlanningScore
from timefold.solver.score import HardSoftScore

@dataclass
class Technician:
    id: Annotated[int, PlanningId]
    pesel: str
    name: str
    rbh_per_week: int
    rbh_per_year: float
    rbh_week_plan: float
    selected_rbh: float
    free_rbh: float
    iums: Set[str]

    def has_ium(self, ium: str) -> bool:
        return ium in self.iums

    def __str__(self) -> str:
        return f"Technician(id={self.id}, name={self.name}, pesel={self.pesel}, " \
               f"rbh_per_week={self.rbh_per_week}, rbh_per_year={self.rbh_per_year}, " \
               f"rbh_week_plan={self.rbh_week_plan}, selected_rbh={self.selected_rbh}, " \
               f"free_rbh={self.free_rbh}, iums={self.iums})"

@planning_entity
@dataclass
class Device:
    index: Annotated[int, PlanningId]
    ind_rek: str
    ium: str
    nazwa: str
    typ: str
    nr_fab: str
    norma_rbh: float
    data_dostawy: str
    uzytkownik: str
    pesel: Annotated[Technician | None, PlanningVariable(allows_unassigned=True)] = field(default=None)
    #pesel: Annotated[Technician | None, PlanningVariable] = field(default=None)

    def __str__(self) -> str:
        technician_str = str(self.pesel) if self.pesel else "None"
        return (f"Device(index={self.index}, ind_rek={self.ind_rek}, ium={self.ium}, "
                f"nazwa={self.nazwa}, typ={self.typ}, nr_fab={self.nr_fab}, "
                f"norma_rbh={self.norma_rbh}, data_dostawy={self.data_dostawy}, "
                f"uzytkownik={self.uzytkownik}, assigned_technician={technician_str})")

@planning_solution
@dataclass
class DeviceSchedule:
    id: str
    technician_list: Annotated[List[Technician], ProblemFactCollectionProperty, ValueRangeProvider]
    device_list: Annotated[List[Device], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)

    def __str__(self):
        return (
            f"DeviceSchedule("
            f"id={self.id},\n"
            f"technician_list={self.technician_list},\n"
            f"device_list={self.device_list},\n"
            f"score={self.score}"
            f")"
        )



# Function to generate devices from provided data
def generate_devices(devices: DataFrame) -> List[Device]:
    return [_create_device(index, row) for index, row in devices.iterrows()]


# Function to create a device
def _create_device(index: int, row: Dict) -> Device:
    data_dostawy = row['u_data_p']
    data_dostawy = data_dostawy.strftime('%Y-%m-%d') if isinstance(data_dostawy, datetime) else data_dostawy

    pesel_value = row.get('k_do_pesel', None)
    technician = next((t for t in technicians_list if t.pesel == pesel_value), None) if pd.notna(pesel_value) else None

    #print(f"Creating Device: index={index}, norma_rbh={row.get('p_norma_k', 'Missing')}")

    return Device(
        index=index,
        ind_rek=row['p_ind_rek'],
        ium=row['ium'],
        nazwa=row['nazwa'],
        typ=row['p_typ'],
        nr_fab=row['p_nr_fab'],
        norma_rbh=row['p_norma_k'],
        data_dostawy=data_dostawy,  # Ensure it's a string
        uzytkownik=row['u_nazwa_s'],
        pesel=technician  # Assign the Technician object or None
    )


# Function to generate technicians from provided data
def generate_technicians(technicians: DataFrame) -> List[Technician]:
    return [_create_technician(index, row) for index, row in technicians.iterrows()]


# Function to create a technician
from typing import Set


def _create_technician(index: int, row: Dict[str, Union[int, str, float, Set[str]]]) -> Technician:
    return Technician(
        id=index,
        pesel=str(row['l_pesel']),
        name=str(row['l_nazw_im']),
        rbh_per_week=int(row['l_pr_thn']),
        rbh_per_year=float(row['l_norma_p']),
        rbh_week_plan=float(row['rbh_week_plan']),
        selected_rbh=float(row['selected_rbh']),
        free_rbh=float(row['free_rbh']),
        iums=set(row['iums'])
    )


# Function to print datatables
def print_datatables(devices: List[Device], technicians: List[Technician]):
    for device in devices:
        print(device)
    for technician in technicians:
        print(technician)


# creating lists
devices_list = generate_devices(devices_in_bok_to_select)
technicians_list = generate_technicians(technicians)

# processing
if __name__ == '__main__':
    print_datatables(devices_list, technicians_list)
"""
solution:
Technician(id=6, name=Karbownik Joanna) total norma_rbh: 50.0
Technician(id=11, name=Kubaczyk Krzysztof) total norma_rbh: 28.0
Technician(id=17, name=Skoniecka Agnieszka) total norma_rbh: 24.0
Technician(id=19, name=Szewczyk Mariusz) total norma_rbh: 28.0
Technician(id=2, name=Fodemski Dominik) total norma_rbh: 4.0
Technician(id=4, name=Kalinowski Jarosław) total norma_rbh: 2.0
Technician(id=0, name=Bugaj Ireneusz) total norma_rbh: 102.0
Technician(id=5, name=Kaliś Krzysztof) total norma_rbh: 12.5
Technician(id=1, name=Byszewski Dariusz) total norma_rbh: 120.0
Technician(id=10, name=Krzycholik Dariusz) total norma_rbh: 48.0
"""