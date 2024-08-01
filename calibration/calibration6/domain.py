from datetime import datetime, timedelta, time
from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore
from dataclasses import dataclass, field
from typing import Annotated, List

@dataclass
class Technician:
    id: Annotated[int, PlanningId]
    name: str
    skills: set
    work_schedule: dict  # Example: {'2024-07-01': ('07:00', 480)}

    def has_skill(self, skill):
        return skill in self.skills

    def is_available(self, date_str, start_time):
        if date_str in self.work_schedule:
            work_start, work_duration = self.work_schedule[date_str]
            work_end = datetime.strptime(work_start, "%H:%M") + timedelta(minutes=work_duration)
            return work_start <= start_time < work_end.time()
        return False

    def __str__(self):
        return f"Technician(id={self.id}, name={self.name}, skills={self.skills})"

@dataclass
class Workstation:
    id: Annotated[int, PlanningId]
    name: str
    supported_device_types: dict  # Example: {'type1': 3}

    def supports_device_type(self, device_type):
        return device_type in self.supported_device_types

    def get_capacity(self, device_type):
        return self.supported_device_types.get(device_type, 0)

    def __str__(self):
        return f"Workstation(id={self.id}, name={self.name}, supported_device_types={self.supported_device_types})"

@dataclass
class Timeslot:
    id: Annotated[int, PlanningId]
    date: str
    start_time: time
    end_time: time

    def __str__(self):
        return (
            f"Timeslot("
            f"id={self.id}, "
            f"date={self.date}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time})"
        )

@planning_entity
@dataclass
class Device:
    id: Annotated[int, PlanningId]
    name: str
    type: str
    required_skill: str
    serial_number: str
    delivery_date: str
    time_for_service: float
    technician: Annotated[Technician | None, PlanningVariable(value_range_provider_refs=["technicianRange"])] = field(default=None)
    workstation: Annotated[Workstation | None, PlanningVariable(value_range_provider_refs=["workstationRange"])] = field(default=None)
    timeslot: Annotated[Timeslot | None, PlanningVariable(value_range_provider_refs=["timeslotRange"])] = field(default=None)

    def __str__(self):
        return (
            f"Device("
            f"id={self.id}, "
            f"name={self.name}, "
            f"type={self.type}, "
            f"required_skill={self.required_skill}, "
            f"serial_number={self.serial_number}, "
            f"delivery_date={self.delivery_date}, "
            f"time_for_service={self.time_for_service}, "
            f"technician={self.technician}, "
            f"workstation={self.workstation}, "
            f"timeslot={self.timeslot}"
            f")"
        )

@planning_solution
@dataclass
class DeviceSchedule:
    id: str
    timeslot_list: Annotated[List[Timeslot], ProblemFactCollectionProperty, ValueRangeProvider]
    technician_list: Annotated[List[Technician], ProblemFactCollectionProperty, ValueRangeProvider]
    workstation_list: Annotated[List[Workstation], ProblemFactCollectionProperty, ValueRangeProvider]
    device_list: Annotated[List[Device], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)

    def __str__(self):
        return (
            f"DeviceSchedule("
            f"id={self.id},\n"
            f"timeslot_list={self.timeslot_list},\n"
            f"technician_list={self.technician_list},\n"
            f"workstation_list={self.workstation_list},\n"
            f"device_list={self.device_list},\n"
            f"score={self.score}"
            f")"
        )
