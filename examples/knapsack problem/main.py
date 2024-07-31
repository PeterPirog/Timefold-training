from datetime import timedelta
from timefold.solver import SolverFactory
from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration
from constraints import define_constraints
from domain import Item, SackChoice, Bagpack

def generate_problem():
    sackchoice_list = [
        SackChoice(id='choice1', is_selected=False),
        SackChoice(id='choice2', is_selected=True),
    ]

    item_list = [
        Item(id="Item1", value=60.0, weight=10.0, number_of_items=1),
        Item(id="Item2", value=100.0, weight=20.0, number_of_items=1),
        Item(id="Item3", value=120.0, weight=30.0, number_of_items=1),
        Item(id="Item4", value=80.0, weight=40.0, number_of_items=1),
        Item(id="Item5", value=50.0, weight=50.0, number_of_items=1),
        Item(id="Item6", value=70.0, weight=60.0, number_of_items=1),
        Item(id="Item7", value=90.0, weight=70.0, number_of_items=1),
        Item(id="Item8", value=110.0, weight=80.0, number_of_items=1),
        Item(id="Item9", value=130.0, weight=90.0, number_of_items=1),
        Item(id="Item10", value=140.0, weight=100.0, number_of_items=1)
    ]
    return Bagpack("bagpack1", sackchoice_list, item_list)

def main():
    problem = generate_problem()

    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=Bagpack,
            entity_class_list=[Item],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            ),
            termination_config=TerminationConfig(
                spent_limit=Duration(seconds=30)
            )
        )
    )

    solver = solver_factory.build_solver()
    solution = solver.solve(problem)

    print_solution(solution)

def print_solution(solution):
    print("Schedule:")
    for item in solution.items:
        print(f"Item: {item.id}, Value: {item.value}, Weight: {item.weight}, Selected: {item.choice.is_selected if item.choice else 'N/A'}")

if __name__ == "__main__":
    main()
