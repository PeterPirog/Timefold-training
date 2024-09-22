import pandas as pd
from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration
from timefold.solver import SolverFactory
from constraints import define_constraints
from domain import DeviceSchedule, Device, generate_devices, generate_technicians
from tools.df_merges import get_technician_and_device_data
from timefold.solver.score import HardSoftScore

def generate_problem(technicians_list, devices_list):
    #return DeviceSchedule("schedule1", [technicians_list[2], technicians_list[24],technicians_list[23]], devices_list)
    #return DeviceSchedule("schedule1", technicians_list[:2], devices_list)
    return DeviceSchedule("schedule1", technicians_list, devices_list)

def print_solution(solution: DeviceSchedule, extended: bool = False, save_to_excel: bool = False, excel_file: str = "solution.xlsx"):
    """
    Wyświetla rozwiązanie problemu optymalizacji z dokładnym sprawdzeniem przypisań.
    W zależności od parametru 'extended', wyświetla pełne lub skrócone informacje o technikach.
    Jeśli save_to_excel=True, zapisuje wynik do pliku Excel z wszystkimi kolumnami Device, posortowany po 'dni_w_om'.
    """
    print("\nOptimized Device Assignments:")
    summary = {}
    devices_data = []

    for device in solution.device_list:
        technician = device.technician
        if technician:
            if extended:
                technician_info = (f"Technician(id={technician.id}, name={technician.name}, "
                                   f"rbh_do_zaplanowania={technician.rbh_do_zaplanowania})")
            else:
                technician_info = technician.name
        else:
            technician_info = "None"

        # Dodawanie informacji do wyświetlenia
        print(f"Device(index={device.index}, ium={device.ium}, nazwa={device.nazwa}, "
              f"typ={device.typ}, assigned_technician={technician_info}, rbh_norma={device.rbh_norma})")

        # Dodawanie danych do zapisu w Excelu (wszystkie kolumny z klasy Device)
        devices_data.append({
            "Device Index": device.index,
            "Days in OM": device.dni_w_om,  # Przeniesiona kolumna 'dni_w_om' na drugą pozycję
            "IUM": device.ium,
            "Device Name": device.nazwa,
            "Device Type": device.typ,
            "Serial Number": device.nr_fabryczny,
            "RBH Norma": device.rbh_norma,
            "User": device.uzytkownik,
            "Technician": technician_info
        })

        # Sumowanie RBH dla technika
        if technician:
            if technician.id not in summary:
                summary[technician.id] = {'name': technician.name, 'total_norma_rbh': 0, 'rbh_do_zaplanowania': technician.rbh_do_zaplanowania}
            summary[technician.id]['total_norma_rbh'] += device.rbh_norma

    # Wyświetlanie podsumowania dla każdego technika i ścisła weryfikacja przypisań
    for technician_id, technician_info in summary.items():
        total_rbh = technician_info['total_norma_rbh']
        rbh_do_zaplanowania = technician_info['rbh_do_zaplanowania']
        if total_rbh > rbh_do_zaplanowania:
            print(f"[ERROR] Technician(id={technician_id}, name={technician_info['name']}) "
                  f"total norma_rbh: {total_rbh} exceeds available hours: {rbh_do_zaplanowania}")
        else:
            print(f"Technician(id={technician_id}, name={technician_info['name']}) "
                  f"total norma_rbh: {total_rbh}, rbh_do_zaplanowania: {rbh_do_zaplanowania}")

    print(f"\nSolution score: {solution.score}")
    print(f"Number of broken hard constraints: {-solution.score.hard_score}")

    # Zapis do Excela, jeśli save_to_excel=True
    if save_to_excel:
        # Tworzenie DataFrame i sortowanie po kolumnie 'Days in OM' (dni_w_om)
        df = pd.DataFrame(devices_data)
        df_sorted = df.sort_values(by='Days in OM', ascending=False)

        # Zapis do pliku Excel z dodanym filtrem
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df_sorted.to_excel(writer, index=False, sheet_name='Device Schedule')

            # Pobranie workbook i worksheet z xlsxwriter, aby dodać filtr
            workbook = writer.book
            worksheet = writer.sheets['Device Schedule']

            # Dodanie filtra na pierwszym wierszu
            worksheet.autofilter(0, 0, df_sorted.shape[0], df_sorted.shape[1] - 1)

        print(f"\nSolution saved to {excel_file}")

def on_best_solution_change(event):
    """
    Funkcja wywoływana po znalezieniu najlepszego rozwiązania.
    """
    best_solution = event.new_best_solution
    print(f"\nNew Best Solution Found! Score: {best_solution.score}")
    print(f"Hard score: {-best_solution.score.hard_score}, Soft score: {best_solution.score.soft_score}")

if __name__ == '__main__':
    # Pobierz dane techników i urządzeń
    technicians, devices_in_bok_to_assign = get_technician_and_device_data(use_archive_data=True)
    technicians_list = generate_technicians(technicians)
    devices_list = generate_devices(devices_in_bok_to_assign)

    # Konfiguracja solvera
    solver_factory = SolverFactory.create(
        SolverConfig(
            solution_class=DeviceSchedule,
            entity_class_list=[Device],
            score_director_factory_config=ScoreDirectorFactoryConfig(
                constraint_provider_function=define_constraints  # Włączanie ograniczeń
            ),
            termination_config=TerminationConfig(
                best_score_limit="0hard/978soft",  # Solver będzie dążył do osiągnięcia wyższej jakości rozwiązania.
                spent_limit=Duration(minutes=4*60)
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

    # Wyświetlenie rozwiązania i zapis do Excela
    print_solution(solution, extended=False, save_to_excel=True, excel_file="device_schedule.xlsx")
