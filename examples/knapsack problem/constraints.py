from timefold.solver.score import (constraint_provider, HardSoftScore, ConstraintFactory, Constraint)
from domain import Bagpack, Item

weight_limit = 67

@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        maximize_value(constraint_factory),
       # weight_constraint(constraint_factory),
    ]

def maximize_value(constraint_factory: ConstraintFactory) -> Constraint:
    # Maksymalizacja sumarycznej wartości wybranych elementów.
    return (constraint_factory
            .for_each(Item)
            .filter(lambda item: item.choice is not None and item.choice.is_selected)
            .reward(HardSoftScore.ONE_SOFT, lambda item: item.value)
            .as_constraint("Maximize value"))

def weight_constraint(constraint_factory: ConstraintFactory) -> Constraint:
    # Suma wag wybranych elementów musi być mniejsza niż weight_limit.
    return (constraint_factory
            .for_each(Item)
            .filter(lambda item: item.choice is not None and item.choice.is_selected)
            .group_by(lambda item: None, ConstraintFactory.sum(lambda item: item.weight))
            .filter(lambda total_weight: total_weight > weight_limit)
            .penalize(HardSoftScore.ONE_HARD, lambda total_weight: total_weight - weight_limit)
            .as_constraint("Weight limit"))
