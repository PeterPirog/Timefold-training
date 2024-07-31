from datetime import datetime, timedelta, time
from functools import reduce
from timefold.solver.config import SolverConfig, ScoreDirectorFactoryConfig, TerminationConfig, Duration
from timefold.solver import SolverFactory
from constraints import define_constraints  # Upewnij się, że to jest odpowiedniego typu (klasa/funkcja)
from domain import DeviceSchedule, Device, Technician, Workstation, Timeslot

def generate_problem(window_width_minutes=30):
    timeslot_list = []
    start_date = datetime(2024, 7, 1)
    end_date = datetime(2024, 7, 3)
    current_id = 1

    while start_date <= end_date:
        for hour in range(7, 15):
            start_time = datetime.combine(start_date, time(hour, 0))
            end_time = start_time + timedelta(minutes=window_width_minutes)
            timeslot_list.append(Timeslot(current_id, start_date.strftime("%A"), start_time.time(), end_time.time()))
            current_id += 1
        start_date += timedelta(days=1)

    technician_list = [
        Technician(1, "John", {"skill1", "skill2"}),
        Technician(2, "Doe", {"skill1"}),
        Technician(3, "Smith", {"skill1", "skill2"})
    ]
    workstation_list = [
        Workstation(1, "WS1", {"type1"}),
        Workstation(2, "WS2", {"type2"}),
        Workstation(3, "WS3", {"type1", "type2"})
    ]
    device_list = [
        Device(1, "Device1", "type1", "skill1", "SN1", "20230701"),
        Device(2, "Device2", "type1", "skill1", "SN2", "20230702"),
        Device(3, "Device3", "type2", "skill2", "SN3", "20230703"),
        Device(4, "Device4", "type2", "skill2", "SN4", "20230704"),
        Device(5, "Device5", "type2", "skill2", "SN5", "20230705"),
        Device(6, "Device6", "type2", "skill2", "SN6", "20230706"),
        Device(7, "Device7", "type2", "skill2", "SN7", "20230707"),
        Device(8, "Device8", "type2", "skill2", "SN8", "20230708"),
        Device(9, "Device9", "type2", "skill2", "SN9", "20230709"),
        Device(10, "Device10", "type2", "skill2", "SN10", "20230710")
    ]
    return DeviceSchedule("schedule1", timeslot_list, technician_list, workstation_list, device_list)


def print_schedule(schedule: DeviceSchedule):
    technician_list = schedule.technician_list
    workstation_list = schedule.workstation_list
    task_list = schedule.device_list
    slot_task_map = dict()

    total_days = 0
    completed_tasks = 0

    for task in task_list:
        if task.timeslot:
            timeslot_id = task.timeslot.id
            if timeslot_id not in slot_task_map:
                slot_task_map[timeslot_id] = []
            slot_task_map[timeslot_id].append(task)

            delivery_date = datetime.strptime(task.delivery_date, "%Y%m%d").date()
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            first_monday = datetime(2024, 7, 1)
            timeslot_date = first_monday + timedelta(days=days_of_week.index(task.timeslot.day_of_week))
            total_days += (timeslot_date.date() - delivery_date).days
            completed_tasks += 1

    average_completion_time = total_days / completed_tasks if completed_tasks > 0 else 0

    # Print header row
    header_row = "| {:<10} |".format("Date")
    for tech in technician_list:
        header_row += " {:<10} |".format(tech.name)
    print("|" + "------------|" * (len(technician_list) + 1))
    print(header_row)
    print("|" + "------------|" * (len(technician_list) + 1))

    for slot in schedule.timeslot_list:
        # Extract the date and time from the start_time attribute
        start_date_time = datetime.combine(datetime(2024, 7, 1).date(), slot.start_time)
        date_str = start_date_time.strftime("%Y-%m-%d")
        time_str = start_date_time.strftime("%H:%M")
        day_str = slot.day_of_week

        # Print date
        out = "| {:<10} |".format(date_str)
        for _ in technician_list:
            out += " {:<10} |".format("")
        print(out)

        # Print time
        out = "| {:<10} |".format(time_str)
        for tech in technician_list:
            tasks = slot_task_map.get(slot.id, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += " {:<10} |".format("")
            else:
                out += " {:<10} |".format(reduce(lambda a, b: a + "," + b, map(lambda t: t.name, tech_tasks)))
        print(out)

        # Print day of week
        out = "| {:<10} |".format(day_str)
        for _ in technician_list:
            out += " {:<10} |".format("")
        print(out)

        # Print workstation
        out = "| {:<10} |".format("")
        for tech in technician_list:
            tasks = slot_task_map.get(slot.id, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += " {:<10} |".format("")
            else:
                out += " {:<10} |".format(
                    reduce(lambda a, b: a + "," + b, map(lambda t: t.workstation.name, tech_tasks)))
        print(out)

        # Print device type
        out = "| {:<10} |".format("")
        for tech in technician_list:
            tasks = slot_task_map.get(slot.id, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += " {:<10} |".format("")
            else:
                out += " {:<10} |".format(reduce(lambda a, b: a + "," + b, map(lambda t: t.type, tech_tasks)))
        print(out)

        # Print required skill
        out = "| {:<10} |".format("")
        for tech in technician_list:
            tasks = slot_task_map.get(slot.id, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += " {:<10} |".format("")
            else:
                out += " {:<10} |".format(reduce(lambda a, b: a + "," + b, map(lambda t: t.required_skill, tech_tasks)))
        print(out)

        # Print serial number
        out = "| {:<10} |".format("")
        for tech in technician_list:
            tasks = slot_task_map.get(slot.id, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += " {:<10} |".format("")
            else:
                out += " {:<10} |".format(reduce(lambda a, b: a + "," + b, map(lambda t: t.serial_number, tech_tasks)))
        print(out)

        # Print delivery date
        out = "| {:<10} |".format("")
        for tech in technician_list:
            tasks = slot_task_map.get(slot.id, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += " {:<10} |".format("")
            else:
                out += " {:<10} |".format(reduce(lambda a, b: a + "," + b, map(lambda t: t.delivery_date, tech_tasks)))
        print(out)

        print("|" + "------------|" * (len(technician_list) + 1))

    print(f"Average completion time: {average_completion_time:.2f} days")

    unassigned_tasks = list(filter(lambda
                                       unassigned_task: unassigned_task.timeslot is None or unassigned_task.technician is None or unassigned_task.workstation is None,
                                   task_list))
    if len(unassigned_tasks) > 0:
        print()
        print("Unassigned tasks")
        for task in unassigned_tasks:
            technician_name = task.technician.name if task.technician else "No Technician"
            workstation_name = task.workstation.name if task.workstation else "No Workstation"
            print(
                f" {task.name} - {technician_name} - {workstation_name} - {task.type} - {task.required_skill} - {task.serial_number} - {task.delivery_date}")

solver_factory = SolverFactory.create(
    SolverConfig(
        solution_class=DeviceSchedule,
        entity_class_list=[Device],
        score_director_factory_config=ScoreDirectorFactoryConfig(
            constraint_provider_function=define_constraints  # Upewnij się, że define_constraints jest funkcją
        ),
        termination_config=TerminationConfig(
            spent_limit=Duration(seconds=30)  # lub Duration(seconds=30), upewnij się, że Duration jest poprawnie używane
        )
    )
)

solution = solver_factory.build_solver().solve(generate_problem())

print_schedule(solution)
