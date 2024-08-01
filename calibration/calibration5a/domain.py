from datetime import datetime, timedelta, time
from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore
from dataclasses import dataclass, field
from typing import Annotated

from timefold.solver.domain import ShadowVariable, VariableListener

@dataclass
class Technician:
    id: Annotated[int, PlanningId]
    name: str
    skills: set

    def has_skill(self, skill):
        return skill in self.skills

    def __str__(self):
        return f"Technician(id={self.id}, name={self.name}, skills={self.skills})"

@dataclass
class Workstation:
    id: Annotated[int, PlanningId]
    name: str
    supported_device_types: set

    def supports_device_type(self, device_type):
        return device_type in self.supported_device_types

    def __str__(self):
        return f"Workstation(id={self.id}, name={self.name}, supported_device_types={self.supported_device_types})"

@dataclass
class Timeslot:
    id: Annotated[int, PlanningId]
    day_of_week: str
    start_time: time
    end_time: time

    def __str__(self):
        return (
            f"Timeslot("
            f"id={self.id}, "
            f"day_of_week={self.day_of_week}, "
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
    technician: Annotated[Technician | None, PlanningVariable] = field(default=None)
    workstation: Annotated[Workstation | None, PlanningVariable] = field(default=None)
    timeslot: Annotated[Timeslot | None, PlanningVariable] = field(default=None)

    def __str__(self):
        return (
            f"Device("
            f"id={self.id}, "
            f"name={self.name}, "
            f"type={self.type}, "
            f"required_skill={self.required_skill}, "
            f"serial_number={self.serial_number}, "
            f"delivery_date={self.delivery_date}, "
            f"technician={self.technician}, "
            f"workstation={self.workstation}, "
            f"timeslot={self.timeslot}"
            f")"
        )

@planning_solution
@dataclass
class DeviceSchedule:
    id: str
    timeslot_list: Annotated[list[Timeslot], ProblemFactCollectionProperty, ValueRangeProvider]
    technician_list: Annotated[list[Technician], ProblemFactCollectionProperty, ValueRangeProvider]
    workstation_list: Annotated[list[Workstation], ProblemFactCollectionProperty, ValueRangeProvider]
    device_list: Annotated[list[Device], PlanningEntityCollectionProperty]
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

