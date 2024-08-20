from timefold.solver.score import constraint_provider, HardSoftScore, ConstraintFactory, Joiners, ConstraintCollectors
from domain import Device, Technician
from datetime import datetime

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # HARD
        technician_capacity_hard(constraint_factory),
        technician_skill_conflict(constraint_factory),
        # SOFT
        #technician_capacity_soft(constraint_factory),
        #prioritize_earlier_deliveries(constraint_factory),
        assign_technician_soft_constraint(constraint_factory),
        #penalize_unnecessary_assignment(constraint_factory),
    ]


def technician_skill_conflict(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.pesel is not None and not device.pesel.has_ium(device.ium))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician skill conflict"))
def technician_capacity_soft(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .join(Technician, Joiners.equal(lambda device: device.pesel, lambda technician: technician))
            .group_by(lambda device, technician: technician,  # Grupowanie według Technika
                      ConstraintCollectors.sum(lambda device, technician: device.norma_rbh))  # Sumowanie norma_rbh dla każdego Technika
            .filter(lambda technician, total_norma_rbh: total_norma_rbh > technician.free_rbh)  # Filtracja przekroczeń limitu free_rbh
            .penalize(HardSoftScore.ONE_SOFT,  # Zastosowanie kary miękkiej
                      lambda technician, total_norma_rbh: total_norma_rbh - technician.free_rbh)  # Kara proporcjonalna do przekroczenia
            .as_constraint("Technician capacity (soft constraint)"))



def technician_capacity_hard(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .join(Technician, Joiners.equal(lambda device: device.pesel, lambda technician: technician))
            .group_by(lambda device, technician: technician,  # Group by Technician
                      ConstraintCollectors.sum(lambda device,technician: device.norma_rbh))  # Sum norma_rbh for each Technician
            .filter(lambda technician, total_norma_rbh: capacity_filter_debug(technician,total_norma_rbh))  # Apply capacity filter
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician capacity"))

def capacity_filter_debug(technician, total_norma_rbh):
    if total_norma_rbh > technician.free_rbh:
        pass
        # print(f"Kombinacja wyzwalająca: Technician {technician.name}, total_norma_rbh: {total_norma_rbh}, free_rbh: {technician.free_rbh:.2f}")
    return total_norma_rbh > technician.free_rbh

def assign_technician_soft_constraint(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.pesel is not None)  # Urządzenie ma przypisanego technika
            .reward(HardSoftScore.ONE_SOFT)  # Mniejsza nagroda za przypisanie technika
            .as_constraint("Assign technician to as many devices as possible"))

def prioritize_earlier_deliveries(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.pesel is not None)  # Tylko przydzielone przyrządy
            .reward(HardSoftScore.ONE_SOFT,
                    lambda device: days_until_delivery(device.data_dostawy))  # Nagroda za wcześniejsze przypisanie
            .as_constraint("Prioritize earlier deliveries"))

def days_until_delivery(data_dostawy: str) -> int:
    print(f'data_dostawy={data_dostawy}')
    today = datetime.now()#.date()
    print(f'today={today}')
    delivery_date = datetime.strptime(data_dostawy, "%Y-%m-%d").date()
    print(f'delivery_date={delivery_date}')
    return max(0, (today - delivery_date).days)



"""

def technician_capacity(constraint_factory: ConstraintFactory):
    return (constraint_factory
            .for_each(Device)
            .join(Technician, Joiners.equal(lambda device: device.pesel, lambda technician: technician.pesel))
            .group_by(lambda device, technician: technician,  # Group by Technician
                      ConstraintCollectors.sum(
                          (lambda device, technician: device.norma_rbh)))  # Sum norma_rbh for each Technician
            .filter(
        (lambda technician, total_norma_rbh: total_norma_rbh > 20.0))  # Apply capacity filter technician.free_rbh
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician capacity"))
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