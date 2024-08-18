from timefold.solver.score import constraint_provider, HardSoftScore, ConstraintFactory, Joiners, ConstraintCollectors
from rbh_solver.domain import Device, Technician


@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # HARD
        #technician_capacity(constraint_factory),
        technician_skill_conflict(constraint_factory),
        # SOFT
        #assign_technician_soft_constraint(constraint_factory),
        #penalize_unnecessary_assignment(constraint_factory),
    ]


def technician_skill_conflict(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.pesel is not None and not device.pesel.has_ium(device.ium))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician skill conflict"))


def technician_capacity(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .join(Technician, Joiners.equal(lambda device: device.pesel, lambda technician: technician.pesel))
            .group_by(lambda device, technician: technician,  # Group by Technician
                      ConstraintCollectors.sum(
                          (lambda device, technician: device.norma_rbh)))  # Sum norma_rbh for each Technician
            .filter(
        (lambda technician, total_norma_rbh: total_norma_rbh > technician.free_rbh))  # Apply capacity filter
            .penalize(HardSoftScore.ONE_HARD,(lambda technician, total_norma_rbh: total_norma_rbh - technician.free_rbh))
            #.penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician capacity"))

def assign_technician_soft_constraint(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.pesel is not None)  # Urządzenie ma przypisanego technika
            .reward(HardSoftScore.ONE_SOFT)  # Mniejsza nagroda za przypisanie technika
            .as_constraint("Assign technician to as many devices as possible"))

def penalize_unnecessary_assignment(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.pesel is not None and device.norma_rbh > device.pesel.free_rbh)
            .penalize(HardSoftScore.ONE_SOFT)  # Kara za niekorzystne przypisanie
            .as_constraint("Penalize unnecessary technician assignment"))



"""
def technician_capacity(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .join(Technician, Joiners.equal(lambda device: device.pesel, lambda technician: technician.pesel))
            .group_by(lambda device, technician: technician,  # Group by Technician
                      ConstraintCollectors.sum(
                          (lambda device, technician: device.norma_rbh)))  # Sum norma_rbh for each Technician
            .filter(
        (lambda technician, total_norma_rbh: total_norma_rbh > technician.free_rbh))  # Apply capacity filter
            .penalize(HardSoftScore.ONE_HARD,
                      (lambda technician, total_norma_rbh: total_norma_rbh - technician.free_rbh))
            .as_constraint("Technician capacity"))

"""