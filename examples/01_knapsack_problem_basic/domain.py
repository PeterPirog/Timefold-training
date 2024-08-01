from dataclasses import dataclass, field
from typing import Annotated

from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore


@dataclass
class SackChoice:
    id: str = field(default=None)
    is_selected: bool = field(default=False)

    def __str__(self):
        return f'SackChoice(id={self.id}, is_selected={self.is_selected})'


@planning_entity
@dataclass
class Item:
    id: Annotated[str, PlanningId]
    value: float
    weight: float
    choice: Annotated[SackChoice | None, PlanningVariable] = field(default=None)

    def __str__(self):
        return f'Item(id={self.id}, value={self.value},weight={self.weight},choice={self.choice} )'


@planning_solution
@dataclass
class Bagpack:
    id: str
    sackchoices: Annotated[list[SackChoice], ProblemFactCollectionProperty, ValueRangeProvider]
    items: Annotated[list[Item], PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)
