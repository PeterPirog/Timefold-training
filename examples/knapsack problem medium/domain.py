from timefold.solver.domain import (planning_entity, planning_solution, PlanningId, PlanningVariable,
                                    PlanningEntityCollectionProperty,
                                    ProblemFactCollectionProperty, ValueRangeProvider,
                                    PlanningScore)
from timefold.solver.score import HardSoftScore
from dataclasses import dataclass, field
from datetime import time
from typing import Annotated


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
    number_of_items: int
    choice: Annotated[SackChoice | None, PlanningVariable] = field(default=None)


@planning_solution
@dataclass
class Bagpack:
    id: str
    sackchoices: Annotated[list[SackChoice],
                         ProblemFactCollectionProperty,
                         ValueRangeProvider]
    items: Annotated[list[Item],
                       PlanningEntityCollectionProperty]
    score: Annotated[HardSoftScore, PlanningScore] = field(default=None)



if __name__ == "__main__":
    choice1 = SackChoice(id=0, is_selected=False)
    choice2 = SackChoice(id=1, is_selected=True)
    print(choice1)

    print(choice1 == choice2)
