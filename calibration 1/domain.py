import datetime
from datetime import time

import optapy
from optapy import problem_fact, planning_id, planning_entity, planning_variable, \
    planning_solution, planning_entity_collection_property, \
    problem_fact_collection_property, value_range_provider, planning_score
from optapy.types import HardSoftScore

@problem_fact
class Technician:
    id: int
    name: str

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"Technician(id={self.id}, name={self.name})"

@problem_fact
class Workstation:
    id: int
    name: str

    def __init__(self, id, name):
        self.id = id
        self.name = name

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return f"Workstation(id={self.id}, name={self.name})"

@problem_fact
class Timeslot:
    id: int
    day_of_week: str
    start_time: datetime.time
    end_time: datetime.time

    def __init__(self, id, day_of_week, start_time, end_time):
        self.id = id
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time

    @planning_id
    def get_id(self):
        return self.id

    def __str__(self):
        return (
            f"Timeslot("
            f"id={self.id}, "
            f"day_of_week={self.day_of_week}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time})"
        )

@planning_entity
class Device:
    id: int
    name: str
    technician: Technician
    workstation: Workstation
    timeslot: Timeslot

    def __init__(self, id, name, technician=None, workstation=None, timeslot=None):
        self.id = id
        self.name = name
        self.technician = technician
        self.workstation = workstation
        self.timeslot = timeslot

    @planning_id
    def get_id(self):
        return self.id

    @planning_variable(Timeslot, ["timeslotRange"])
    def get_timeslot(self):
        return self.timeslot

    def set_timeslot(self, new_timeslot):
        self.timeslot = new_timeslot

    @planning_variable(Technician, ["technicianRange"])
    def get_technician(self):
        return self.technician

    def set_technician(self, new_technician):
        self.technician = new_technician

    @planning_variable(Workstation, ["workstationRange"])
    def get_workstation(self):
        return self.workstation

    def set_workstation(self, new_workstation):
        self.workstation = new_workstation

    def __str__(self):
        return (
            f"Device("
            f"id={self.id}, "
            f"name={self.name}, "
            f"technician={self.technician}, "
            f"workstation={self.workstation}, "
            f"timeslot={self.timeslot}"
            f")"
        )

@planning_solution
class DeviceSchedule:
    timeslot_list: list[Timeslot]
    technician_list: list[Technician]
    workstation_list: list[Workstation]
    device_list: list[Device]
    score: HardSoftScore

    def __init__(self, timeslot_list, technician_list, workstation_list, device_list, score=None):
        self.timeslot_list = timeslot_list
        self.technician_list = technician_list
        self.workstation_list = workstation_list
        self.device_list = device_list
        self.score = score

    @problem_fact_collection_property(Timeslot)
    @value_range_provider("timeslotRange")
    def get_timeslot_list(self):
        return self.timeslot_list

    @problem_fact_collection_property(Technician)
    @value_range_provider("technicianRange")
    def get_technician_list(self):
        return self.technician_list

    @problem_fact_collection_property(Workstation)
    @value_range_provider("workstationRange")
    def get_workstation_list(self):
        return self.workstation_list

    @planning_entity_collection_property(Device)
    def get_device_list(self):
        return self.device_list

    @planning_score(HardSoftScore)
    def get_score(self):
        return self.score

    def set_score(self, score):
        self.score = score

    def __str__(self):
        return (
            f"DeviceSchedule("
            f"timeslot_list={self.timeslot_list},\n"
            f"technician_list={self.technician_list},\n"
            f"workstation_list={self.workstation_list},\n"
            f"device_list={self.device_list},\n"
            f"score={self.score}"
            f")"
        )

def generate_problem():
    timeslot_list = [
        Timeslot(i, day, time(hour), time(hour + 1))
        for i, (day, hour) in enumerate(
            [(day, hour) for day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"] for hour in range(7, 15)], 1
        )
    ]
    technician_list = [
        Technician(1, "Technician 1"),
        Technician(2, "Technician 2"),
        Technician(3, "Technician 3")
    ]
    workstation_list = [
        Workstation(1, "Workstation 1"),
        Workstation(2, "Workstation 2"),
        Workstation(3, "Workstation 3")
    ]
    device_list = [
        Device(i, f"Device {i}") for i in range(1, 11)
    ]
    return DeviceSchedule(timeslot_list, technician_list, workstation_list, device_list)
