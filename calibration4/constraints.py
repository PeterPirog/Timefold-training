from timefold.solver.score import constraint_provider, HardSoftScore, ConstraintFactory, Joiners
from domain import Device

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
    # Prefer to finish all device services as early as possible.
    return (constraint_factory
            .for_each(Device)
            .reward(HardSoftScore.ONE_SOFT, lambda device: device.timeslot.id)
            .as_constraint("Minimize completion time"))
