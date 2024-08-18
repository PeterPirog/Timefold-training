from datetime import datetime, timedelta, time
from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration
from timefold.solver import SolverFactory
from rbh_solver.constraints import define_constraints
from rbh_solver.domain import DeviceSchedule, Device, devices_list, technicians_list

def generate_problem(technicians_list, devices_list):
    return DeviceSchedule("schedule1", technicians_list, devices_list)

def print_solution(solution: DeviceSchedule):
    print("\nOptimized Device Assignments:")

    # Create a summary dictionary to keep track of total norma_rbh per technician
    summary = {}

    for device in solution.device_list:
        print(device)
        technician = device.pesel  # 'pesel' now refers to the Technician assigned to the Device
        technician_info = f"Technician(id={technician.id}, name={technician.name})" if technician else "None"

        if technician:
            # If the technician hasn't been seen before, initialize their total norma_rbh to 0
            if technician.id not in summary:
                summary[technician.id] = {'name': technician.name, 'total_norma_rbh': 0}

            # Add the device's norma_rbh to the technician's total
            summary[technician.id]['total_norma_rbh'] += device.norma_rbh

        print(f"Device(index={device.index}, ind_rek={device.ind_rek}, ium={device.ium}, "
              f"nazwa={device.nazwa}, typ={device.typ}, nr_fab={device.nr_fab}, "
              f"norma_rbh={device.norma_rbh}, data_dostawy={device.data_dostawy}, "
              f"uzytkownik={device.uzytkownik}, assigned_technician={technician_info})")

    # Now print the total for each technician
    for technician_id, technician_info in summary.items():
        print(f"Technician(id={technician_id}, name={technician_info['name']}) total norma_rbh: {technician_info['total_norma_rbh']}")

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
            spent_limit=Duration(seconds=30)
        )
    )
)

solver = solver_factory.build_solver()

# Dodanie nasłuchiwacza najlepszego rozwiązania
solver.add_event_listener(on_best_solution_change)

# Generate the problem instance
problem = generate_problem(technicians_list, devices_list)

# Solve the problem
solution = solver.solve(problem)

# Print the solution
print_solution(solution)
