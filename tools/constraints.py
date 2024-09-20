from timefold.solver.score import constraint_provider, HardSoftScore, ConstraintFactory, Joiners, ConstraintCollectors
from domain import Device, Technician

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        # HARD constraints
        technician_capacity_hard(constraint_factory),
        technician_skill_conflict(constraint_factory),

        # SOFT constraints
        assign_technician_soft_constraint(constraint_factory),
        #prioritize_earlier_deliveries(constraint_factory),
    ]


def technician_skill_conflict(constraint_factory: ConstraintFactory):
    """
    Penalizuje, jeśli technik nie posiada wymaganej umiejętności (IUM) dla przypisanego urządzenia.
    """
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.technician is not None and not device.technician.has_ium(device.ium))
            .penalize(HardSoftScore.ONE_HARD)
            .as_constraint("Technician skill conflict"))


def technician_capacity_hard2(constraint_factory: ConstraintFactory):
    """
    Penalizuje, jeśli całkowita suma rbh_norma urządzeń przypisanych do technika przekracza jego dostępne godziny do zaplanowania.
    """
    return (constraint_factory
            .for_each(Device)
            .join(Technician, Joiners.equal(lambda device: device.technician, lambda technician: technician))
            .group_by(lambda device, technician: technician,  # Grupowanie po techniku
                      ConstraintCollectors.sum(lambda device: device.rbh_norma))  # Sumowanie rbh_norma dla technika
            .filter(lambda technician, total_rbh_norma: total_rbh_norma > technician.rbh_do_zaplanowania)  # Filtr przekroczenia limitu godzin
            .penalize(HardSoftScore.ONE_HARD,
                      lambda technician, total_rbh_norma: total_rbh_norma - technician.rbh_do_zaplanowania)  # Kara proporcjonalna do przekroczenia limitu
            .as_constraint("Technician capacity (hard constraint)"))

def technician_capacity_hard1(constraint_factory: ConstraintFactory):
    return (
        constraint_factory.for_each(Device)
        .group_by(lambda device: device.technician, ConstraintCollectors.sum(lambda device: device.rbh_norma))
        .filter(lambda technician, total_rbh_norma: total_rbh_norma > technician.rbh_do_zaplanowania)
        .penalize(HardSoftScore.ONE_HARD, lambda technician, total_rbh_norma: total_rbh_norma - technician.rbh_do_zaplanowania)
        .as_constraint("Technician capacity")
    )
def technician_capacity_hard(constraint_factory: ConstraintFactory):
    def technician_rbh_exceeded(technician, total_rbh_norma):
        print(f"Technician: {technician.name}, Total RBH: {total_rbh_norma}, Do zaplanowania: {float(technician.rbh_do_zaplanowania)}")
        return total_rbh_norma > technician.rbh_do_zaplanowania

    return (
        constraint_factory.for_each(Device)
        .group_by(lambda device: device.technician, ConstraintCollectors.sum(lambda device: device.rbh_norma))
        .filter(technician_rbh_exceeded)
        .penalize(HardSoftScore.ONE_HARD, lambda technician, total_rbh_norma: total_rbh_norma - technician.rbh_do_zaplanowania)
        .as_constraint("Technician capacity")
    )
def assign_technician_soft_constraint(constraint_factory: ConstraintFactory):
    """
    Nagroda za przypisanie urządzeń do jak największej liczby przyrządów.
    """
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.technician is not None)  # Urządzenie ma przypisanego technika
            .reward(HardSoftScore.ONE_SOFT)  # Nagroda za przypisanie technika
            .as_constraint("Assign technician to as many devices as possible"))


def prioritize_earlier_deliveries(constraint_factory: ConstraintFactory):
    """
    Nagroda za przypisanie urządzeń z wcześniejszymi datami dostawy, dając wyższy priorytet urządzeniom oczekującym dłużej.
    """
    return (constraint_factory
            .for_each(Device)
            .filter(lambda device: device.technician is not None)  # Tylko przypisane urządzenia
            .reward(HardSoftScore.ONE_SOFT,
                    lambda device: days_until_delivery(device.dni_w_om))  # Nagroda za wcześniejsze przypisanie
            .as_constraint("Prioritize earlier deliveries"))


def days_until_delivery(dni_w_om: int) -> int:
    """
    Oblicza liczbę dni od dostawy, im większa liczba dni, tym wyższy priorytet (starsze urządzenia mają wyższy priorytet).
    """
    return dni_w_om
