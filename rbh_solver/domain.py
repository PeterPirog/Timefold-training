from dataclasses import dataclass, field
from typing import Annotated, Set, List, Dict, Union
from datetime import datetime
from pandas import DataFrame
import pandas as pd
from timefold.solver.domain import PlanningId, planning_entity, planning_solution, PlanningVariable, \
    PlanningEntityCollectionProperty, ProblemFactCollectionProperty, ValueRangeProvider, PlanningScore
from timefold.solver.score import HardSoftScore

# Import danych z istniejących skryptów
from tools.df_merges import technicians, devices_in_bok_to_assign


@dataclass
class Technician:
    id: Annotated[int, PlanningId]
    name: str  # zmiana na 'technician'
    rbh_do_zaplanowania: float  # zmiana na 'rbh_do_zaplanowania'
    rbh_przydzielone: float  # zmiana na 'rbh_przydzielone'
    iums: Set[str]  # iums na końcu, zgodnie z wynikami

    def has_ium(self, ium: str) -> bool:
        return ium in self.iums

    def __str__(self) -> str:
        return f"Technician(id={self.id}, name={self.name}, " \
               f"rbh_do_zaplanowania={self.rbh_do_zaplanowania}, " \
               f"rbh_przydzielone={self.rbh_przydzielone}, iums={self.iums})"


@planning_entity
@dataclass
class Device:
    index: Annotated[int, PlanningId]
    ium: str
    nazwa: str
    typ: str
    nr_fabryczny: str  # zmiana na 'nr_fabryczny'
    rbh_norma: float  # zmiana na 'rbh_norma'
    dni_w_om: int
    uzytkownik: str  # zmiana na 'uzytkownik'
    technician: Annotated[Technician | None, PlanningVariable(allows_unassigned=True)] = field(default=None)

    def __str__(self) -> str:
        technician_str = str(self.technician) if self.technician else "None"
        return (f"Device(index={self.index}, ium={self.ium}, "
                f"nazwa={self.nazwa}, typ={self.typ}, nr_fabryczny={self.nr_fabryczny}, "
                f"rbh_norma={self.rbh_norma}, dni_w_om={self.dni_w_om}, "
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
            f"DeviceSchedule(id={self.id},\n"
            f"technician_list={self.technician_list},\n"
            f"device_list={self.device_list},\n"
            f"score={self.score})"
        )


# Funkcja tworząca techników z dataframe
def _create_technician(index: int, row: Dict[str, Union[int, str, float, Set[str]]]) -> Technician:
    return Technician(
        id=index,
        name=row['technician'],  # zmiana na 'technician'
        rbh_do_zaplanowania=row['rbh_do_zaplanowania'],
        rbh_przydzielone=row['rbh_przydzielone'],
        iums=set(row['iums'])  # zestaw unikalnych ium
    )


# Funkcja tworząca urządzenia z dataframe
def _create_device(index: int, row: Dict) -> Device:
    technician_value = row.get('technician', None)
    technician = next((t for t in technicians_list if t.name == technician_value), None) if pd.notna(technician_value) else None

    return Device(
        index=index,
        ium=row['ium'],
        nazwa=row['nazwa'],
        typ=row['typ'],
        nr_fabryczny=row['nr_fabryczny'],
        rbh_norma=row['rbh_norma'],
        dni_w_om=row['dni_w_om'],
        uzytkownik=row['uzytkownik'],
        technician=technician
    )


# Funkcja generująca techników z dataframe
def generate_technicians(technicians: DataFrame) -> List[Technician]:
    return [_create_technician(index, row) for index, row in technicians.iterrows()]


# Funkcja generująca urządzenia z dataframe
def generate_devices(devices: DataFrame) -> List[Device]:
    return [_create_device(index, row) for index, row in devices.iterrows()]


# Funkcja drukująca techników i urządzenia
def print_datatables(devices: List[Device], technicians: List[Technician]):
    for device in devices:
        print(device)
    for technician in technicians:
        print(technician)


# Tworzenie list
devices_list = generate_devices(devices_in_bok_to_assign)  # zmiana na devices_in_bok_to_assign
technicians_list = generate_technicians(technicians)

# Przetwarzanie
if __name__ == '__main__':
    print_datatables(devices_list, technicians_list)
