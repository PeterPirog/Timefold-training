from timefold.solver.score import constraint_provider, HardSoftScore, ConstraintFactory, Joiners
from domain import Device
from datetime import datetime, timedelta


@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        technician_conflict(constraint_factory),
        workstation_conflict(constraint_factory),
        workstation_capacity(constraint_factory),
        technician_skill_conflict(constraint_factory),
        # Soft constraints
        minimize_completion_time(constraint_factory)
    ]


def technician_conflict(constraint_factory: ConstraintFactory):
    # A technician can work on at most one device at the same time.
    return (constraint_factory
            .for_each_unique_pair(Device,
                                  Joiners.equal(lambda device: device.timeslot),
                                  Joiners.equal(lambda device: device.technician))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician conflict"))


def workstation_conflict(constraint_factory: ConstraintFactory):
    # A workstation can accommodate at most one device at the same time.
    return (constraint_factory
            .for_each_unique_pair(Device,
                                  Joiners.equal(lambda device: device.timeslot),
                                  Joiners.equal(lambda device: device.workstation))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Workstation conflict"))


def workstation_capacity(constraint_factory: ConstraintFactory):
    # A workstation can only support a device if it supports the device type.
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: not device.workstation.supports_device_type(device.type))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Unsupported device type"))


def technician_skill_conflict(constraint_factory: ConstraintFactory):
    # A technician can only work on a device if they have the required skill.
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: not device.technician.has_skill(device.required_skill))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician skill conflict"))


def minimize_completion_time(constraint_factory: ConstraintFactory):
    # Minimize the average completion time for all devices.
    def calculate_days_between(device: Device):
        delivery_date = datetime.strptime(device.delivery_date, "%Y%m%d").date()

        # Map day_of_week to a date
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        first_monday = datetime(2024, 7, 1)  # The first Monday of July 2024
        timeslot_date = first_monday + timedelta(days=days_of_week.index(device.timeslot.day_of_week))

        return (timeslot_date.date() - delivery_date).days

    return (constraint_factory
            .for_each(Device)
            .penalize(HardSoftScore.ONE_SOFT, calculate_days_between)
            .as_constraint("Minimize completion time"))
