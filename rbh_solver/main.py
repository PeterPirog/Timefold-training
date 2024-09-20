from datetime import datetime, timedelta, time
from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration
from timefold.solver import SolverFactory
from rbh_solver.constraints import define_constraints
from rbh_solver.domain import DeviceSchedule, Device, devices_list, technicians_list


def generate_problem(technicians_list, devices_list):
    return DeviceSchedule("schedule1", technicians_list, devices_list)


def print_solution(solution: DeviceSchedule, extended: bool = False):
    print("\nOptimized Device Assignments:")

    summary = {}

    for device in solution.device_list:
        technician = device.pesel
        if extended:
            # Print detailed information about the assigned technician
            technician_info = f"Technician(id={technician.id}, name={technician.name}, pesel={technician.pesel}, rbh_per_week={technician.rbh_per_week}, rbh_per_year={technician.rbh_per_year}, rbh_week_plan={technician.rbh_week_plan}, selected_rbh={technician.selected_rbh}, free_rbh={technician.free_rbh}, iums={technician.iums})" if technician else "None"
        else:
            # Print only basic information about the assigned technician
            technician_info = f"Technician(id={technician.id}, name={technician.name})" if technician else "None"

        # Print the device information with the appropriate technician info
        print(f"Device(index={device.index}, ind_rek={device.ind_rek}, ium={device.ium}, "
              f"nazwa={device.nazwa}, typ={device.typ}, nr_fab={device.nr_fab}, "
              f"norma_rbh={device.norma_rbh}, data_dostawy={device.data_dostawy}, "
              f"uzytkownik={device.uzytkownik}, assigned_technician={technician_info})")

        if technician:
            if technician.id not in summary:
                summary[technician.id] = {'name': technician.name, 'total_norma_rbh': 0}
            summary[technician.id]['total_norma_rbh'] += device.norma_rbh

    # Now print the total norma_rbh for each technician
    for technician_id, technician_info in summary.items():
        print(
            f"Technician(id={technician_id}, name={technician_info['name']}) total norma_rbh: {technician_info['total_norma_rbh']}")

    # Display the score which indicates the number of broken hard constraints
    print(f"\nSolution score: {solution.score}")
    print(f"Number of broken hard constraints: {-solution.score.hard_score}")


def on_best_solution_change(event):
    best_solution = event.new_best_solution
    print(f"\nNew Best Solution Found! Score: {best_solution.score}")
    print(f"Hard score: {-best_solution.score.hard_score}, Soft score: {best_solution.score.soft_score}")


    # Konfiguracja solvera
    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=DeviceSchedule,
            entity_class_list=[Device],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints
            ),
            termination_config=TerminationConfig(
                spent_limit=Duration(seconds=60)
            )
        )
    )

    solver = solver_factory.build_solver()

    # Dodanie nasłuchiwacza najlepszego rozwiązania
    solver.add_event_listener(on_best_solution_change)

    # Generate the problem instance
    problem = generate_problem(technicians_list[:10], devices_list)

    # Solve the problem
    solution = solver.solve(problem)

    # Print the solution
    print_solution(solution, extended=False)
