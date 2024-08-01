from functools import reduce

from optapy import solver_factory_create
from optapy.types import SolverConfig, Duration
from domain import DeviceSchedule, Device, generate_problem
from constraints import define_constraints

def print_schedule(schedule: DeviceSchedule):
    technician_list = schedule.technician_list
    workstation_list = schedule.workstation_list
    task_list = schedule.device_list
    slot_task_map = dict()

    for task in task_list:
        if task.timeslot:
            if task.timeslot not in slot_task_map:
                slot_task_map[task.timeslot] = []
            slot_task_map[task.timeslot].append(task)

    print("|" + ("------------|" * (len(technician_list) + 1)))
    print(reduce(lambda a, b: a + b + " | ",
                 map(lambda tech: "{:<10}".format(tech.name)[0:10], technician_list),
                 "|            | "))
    print("|" + ("------------|" * (len(technician_list) + 1)))
    for slot in schedule.timeslot_list:
        out = "| " + (slot.day_of_week[0:3] + " " + str(slot.start_time))[0:10] + " | "
        for tech in technician_list:
            tasks = slot_task_map.get(slot, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += "           | "
            else:
                out += "{:<10}".format(reduce(lambda a, b: a + "," + b,
                                              map(lambda t: t.name, tech_tasks)))[0:10] + " | "
        print(out)
        out = "|            | "
        for tech in technician_list:
            tasks = slot_task_map.get(slot, [])
            tech_tasks = [task for task in tasks if task.technician == tech]
            if len(tech_tasks) == 0:
                out += "           | "
            else:
                out += "{:<10}".format(reduce(lambda a, b: a + "," + b,
                                              map(lambda t: t.workstation.name, tech_tasks)))[0:10] + " | "
        print(out)
        print("|" + ("------------|" * (len(technician_list) + 1)))
    unassigned_tasks = list(
        filter(lambda unassigned_task: unassigned_task.timeslot is None or unassigned_task.technician is None or unassigned_task.workstation is None,
               task_list))
    if len(unassigned_tasks) > 0:
        print()
        print("Unassigned tasks")
        for task in unassigned_tasks:
            technician_name = task.technician.name if task.technician else "No Technician"
            workstation_name = task.workstation.name if task.workstation else "No Workstation"
            print(f" {task.name} - {technician_name} - {workstation_name}")

solver_config = SolverConfig().withEntityClasses(Device) \
    .withSolutionClass(DeviceSchedule) \
    .withConstraintProviderClass(define_constraints) \
    .withTerminationSpentLimit(Duration.ofSeconds(30))

solver = solver_factory_create(solver_config).buildSolver()

solution = solver.solve(generate_problem())

print_schedule(solution)
