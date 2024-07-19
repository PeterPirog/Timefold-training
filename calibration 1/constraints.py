from optapy import constraint_provider
from optapy.score import HardSoftScore
from optapy.constraint import ConstraintFactory, Joiners
from domain import Device

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # Hard constraints
        technician_conflict(constraint_factory),
        workstation_conflict(constraint_factory),
        # Soft constraints
        minimize_completion_time(constraint_factory)
    ]

def technician_conflict(constraint_factory: ConstraintFactory):
    # A technician can work on at most one device at the same time.
    return constraint_factory \
        .for_each(Device) \
        .join(Device,
              Joiners.equal(lambda device: device.timeslot),
              Joiners.equal(lambda device: device.technician),
              Joiners.less_than(lambda device: device.id)
              ) \
        .penalize("Technician conflict", HardSoftScore.ONE_HARD)

def workstation_conflict(constraint_factory: ConstraintFactory):
    # A workstation can accommodate at most one device at the same time.
    return constraint_factory \
        .for_each(Device) \
        .join(Device,
              Joiners.equal(lambda device: device.timeslot),
              Joiners.equal(lambda device: device.workstation),
              Joiners.equal(lambda device: device.id)
              ) \
        .penalize("Workstation conflict", HardSoftScore.ONE_HARD)

def minimize_completion_time(constraint_factory: ConstraintFactory):
    # Prefer to finish all device services as early as possible.
    return constraint_factory \
        .for_each(Device) \
        .reward("Minimize completion time", HardSoftScore.ONE_SOFT,
                lambda device: device.timeslot.id)
