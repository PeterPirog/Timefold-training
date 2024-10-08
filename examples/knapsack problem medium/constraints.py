from timefold.solver.score import (constraint_provider, HardSoftScore, ConstraintFactory, Constraint, ConstraintCollectors, HardMediumSoftScore)
from domain import Bagpack, Item

weight_limit = 200



@constraint_provider
def define_constraints(constraint_factory: ConstraintFactory):
    return [
        weight_constraint(constraint_factory),
        maximize_value(constraint_factory),
        prefer_light_items(constraint_factory),
    ]



def weight_constraint(constraint_factory: ConstraintFactory) -> Constraint:
    # Suma wag wybranych elementów musi być mniejsza niż weight_limit.
    return (constraint_factory
            .for_each(Item)
            .filter(lambda item: item.choice is not None and item.choice.is_selected)
            .group_by(lambda item: None, ConstraintCollectors.sum(lambda item: item.weight))
            .filter(lambda _, total_weight: total_weight > weight_limit)
            .penalize(HardMediumSoftScore.ONE_HARD, lambda _, total_weight: total_weight - weight_limit)
            .as_constraint("Weight limit"))

def maximize_value(constraint_factory: ConstraintFactory) -> Constraint:
    # Maksymalizacja sumarycznej wartości wybranych elementów.
    return (constraint_factory
            .for_each(Item)
            .filter(lambda item: item.choice is not None and item.choice.is_selected)
            .reward(HardMediumSoftScore.ONE_MEDIUM, lambda item: item.value)
            .as_constraint("Maximize value"))

def prefer_light_items(constraint_factory: ConstraintFactory) -> Constraint:
    # Preferencje dla lżejszych przedmiotów.
    return (constraint_factory
            .for_each(Item)
            .filter(lambda item: item.choice is not None and item.choice.is_selected and item.weight < 30)
            .reward(HardMediumSoftScore.ONE_SOFT)
            .as_constraint("Prefer light items"))