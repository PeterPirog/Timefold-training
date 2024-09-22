from dataclasses import dataclass, field
from typing import Annotated, Set, List, Dict, Union
from pandas import DataFrame  # Poprawka: dodanie importu DataFrame
import pandas as pd
from timefold.solver.domain import PlanningId, planning_entity, planning_solution, PlanningVariable, \
    PlanningEntityCollectionProperty, ProblemFactCollectionProperty, ValueRangeProvider, PlanningScore
from timefold.solver.score import HardSoftScore
from tools.df_merges import get_technician_and_device_data


@dataclass
class Technician:
    id: Annotated[int, PlanningId]
    name: str
    rbh_do_zaplanowania: int  # Zmienione z float na int (minuty)
    rbh_przydzielone: int  # Zmienione z float na int (minuty)
    iums: Set[str]

    def has_ium(self, ium: str) -> bool:
        return ium in self.iums

    def __str__(self) -> str:
        return (f"Technician(id={self.id}, name={self.name}, "
                f"rbh_do_zaplanowania={self.rbh_do_zaplanowania} min, "
                f"rbh_przydzielone={self.rbh_przydzielone} min, iums={self.iums})")


@planning_entity
@dataclass
class Device:
    index: Annotated[int, PlanningId]
    ium: str
    nazwa: str
    typ: str
    nr_fabryczny: str
    rbh_norma: int  # Zmienione z float na int (minuty)
    dni_w_om: float
    uzytkownik: str
    technician: Annotated[Technician | None, PlanningVariable(allows_unassigned=True)] = field(default=None)

    def __str__(self) -> str:
        technician_str = str(self.technician) if self.technician else "None"
        return (f"Device(index={self.index}, ium={self.ium}, nazwa={self.nazwa}, "
                f"typ={self.typ}, nr_fabryczny={self.nr_fabryczny}, "
                f"rbh_norma={self.rbh_norma} min, dni_w_om={self.dni_w_om}, "
                f"uzytkownik={self.uzytkownik}, assigned_technician={technician_str})")


@planning_solution
@dataclass
class DeviceSchedule:
    id: str
    technician_list: Annotated[List[Technician], ProblemFactCollectionProperty, ValueRangeProvider]
    device_list: Annotated[List[Device], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)

    def __str__(self):
        return (f"DeviceSchedule(id={self.id},\n"
                f"technician_list={self.technician_list},\n"
                f"device_list={self.device_list},\n"
                f"score={self.score})")


# Funkcja tworząca techników z dataframe
def generate_technicians(technicians: DataFrame) -> List[Technician]:
    """
    Generowanie techników z dataframe, dodanie logów do debugowania.
    """
    technician_list = [
        Technician(
            index,
            row['technician'],
            int(row['rbh_do_zaplanowania'] * 60),  # Konwersja z godzin (float) na minuty (int)
            int(row['rbh_przydzielone'] * 60),  # Konwersja z godzin (float) na minuty (int)
            set(row['iums'])
        )
        for index, row in technicians.iterrows()
    ]
    for technician in technician_list:
        pass
        print(f"Generated Technician: {technician}")
    return technician_list


def generate_devices(devices: DataFrame) -> List[Device]:
    """
    Generowanie urządzeń z dataframe, dodanie logów do debugowania.
    """
    device_list = [
        Device(
            index,
            str(row['ium']).zfill(6),
            row['nazwa'],
            row['typ'],
            row['nr_fabryczny'],
            int(row['rbh_norma'] * 60),  # Konwersja z godzin (float) na minuty (int)
            row['dni_w_om'],
            row['uzytkownik']
        )
        for index, row in devices.iterrows()
    ]
    for device in device_list:
        pass
        # print(f"Generated Device: {device}")
    return device_list


# Funkcja drukująca techników i urządzenia
def print_datatables(devices: List[Device], technicians: List[Technician]):
    for device in devices:
        print(device)
    for technician in technicians:
        print(technician)


# Tworzenie list
technicians, devices_in_bok_to_assign = get_technician_and_device_data(use_archive_data=False)
devices_list = generate_devices(devices_in_bok_to_assign)
technicians_list = generate_technicians(technicians)

# Przetwarzanie
if __name__ == '__main__':
    print_datatables(devices_list, technicians_list)

    # print(f'devices_in_bok_to_assign ={devices_in_bok_to_assign }')
