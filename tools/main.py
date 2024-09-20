from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration
from timefold.solver import SolverFactory
from constraints import define_constraints
from domain import DeviceSchedule, Device, generate_devices, generate_technicians
from tools.df_merges import get_technician_and_device_data

def generate_problem(technicians_list, devices_list):
    """
    Tworzy instancję problemu z listą techników i urządzeń.
    """
    return DeviceSchedule("schedule1", technicians_list, devices_list)

def print_solution(solution: DeviceSchedule, extended: bool = False):
    """
    Wyświetla rozwiązanie problemu optymalizacji.
    """
    print("\nOptimized Device Assignments:")
    summary = {}
    for device in solution.device_list:
        technician = device.technician
        if extended:
            technician_info = (f"Technician(id={technician.id}, name={technician.name}, "
                               f"rbh_do_zaplanowania={technician.rbh_do_zaplanowania}, "
                               f"rbh_przydzielone={technician.rbh_przydzielone}, "
                               f"iums={technician.iums})" if technician else "None")
        else:
            technician_info = f"Technician(id={technician.id}, name={technician.name})" if technician else "None"
        print(f"Device(index={device.index}, ium={device.ium}, nazwa={device.nazwa}, "
              f"typ={device.typ}, nr_fabryczny={device.nr_fabryczny}, "
              f"rbh_norma={device.rbh_norma}, dni_w_om={device.dni_w_om}, "
              f"uzytkownik={device.uzytkownik}, assigned_technician={technician_info})")
        if technician:
            if technician.id not in summary:
                summary[technician.id] = {'name': technician.name, 'total_norma_rbh': 0}
            summary[technician.id]['total_norma_rbh'] += device.rbh_norma
    for technician_id, technician_info in summary.items():
        print(f"Technician(id={technician_id}, name={technician_info['name']}) total norma_rbh: {technician_info['total_norma_rbh']}")
    print(f"\nSolution score: {solution.score}")
    print(f"Number of broken hard constraints: {-solution.score.hard_score}")

def on_best_solution_change(event):
    """
    Funkcja wywoływana po znalezieniu najlepszego rozwiązania.
    """
    best_solution = event.new_best_solution
    print(f"\nNew Best Solution Found! Score: {best_solution.score}")
    print(f"Hard score: {-best_solution.score.hard_score}, Soft score: {best_solution.score.soft_score}")



if __name__ == '__main__':
    if __name__ == '__main__':
        # Pobierz dane techników i urządzeń
        technicians, devices_in_bok_to_assign = get_technician_and_device_data(use_archive_data=True)
        technicians_list = generate_technicians(technicians)
        devices_list = generate_devices(devices_in_bok_to_assign)

        # print(technicians_list)
        # print(devices_list)




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

        # Generowanie instancji problemu
        problem = generate_problem(technicians_list, devices_list)

        # Rozwiązanie problemu
        solution = solver.solve(problem)

        # Wyświetlenie rozwiązania
        print_solution(solution, extended=False)

        """
        """