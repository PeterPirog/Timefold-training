import os

import pandas as pd
from django.apps import apps

from data_utils import populate_table, display_model_data_as_dataframe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django

django.setup()

# Przykład użycia
if __name__ == "__main__":
    # Zmiana nazw klas
    Department = apps.get_model('optylogis', 'Department')
    Project = apps.get_model('optylogis', 'Project')
    EmployeeAssignment = apps.get_model('optylogis', 'EmployeeAssignment')

    # Dane do tabel
    data_departments = {
        'dept_name': ['HR', 'Finance', 'Engineering'],
        'description': ['Human Resources', 'Financial Department', 'Engineering Department']
    }

    data_projects = {
        'name': ['Project X', 'Project Y', 'Project Z'],
        'description': ['Top Secret Project X', 'Top Secret Project Y', 'Top Secret Project Z']
    }

    data_employee_assignments = {
        'dept': ['Finance', 'Finance', 'HR'],
        'proj': ['Project X', 'Project X', 'Project Miss'],  # 'Project Miss' nie istnieje w tabeli Project
        'role': ['Manager', 'Analyst', 'Recruiter'],
        'proj_description': ['Lead', 'Support', 'Lead']
    }

    # Tworzenie DataFrame'ów
    df_departments = pd.DataFrame(data_departments)
    df_projects = pd.DataFrame(data_projects)
    df_employee_assignments = pd.DataFrame(data_employee_assignments)

    # Mapowanie kolumn DataFrame na pola Django modelu
    department_mapping = {
        'dept_name': 'name',
        'description': 'description'
    }

    project_mapping = {
        'name': 'name',
        'description': 'description'
    }

    employee_assignment_mapping = {
        'dept': 'department',
        'proj': 'project',
        'role': 'role',
        'proj_description': 'project_description'
    }

    # Wyczyść i wypełnij tabele Department i Project, resetując indeksy
    populate_table(Department, df_departments, clear=True, column_mapping=department_mapping)
    populate_table(Project, df_projects, clear=True, column_mapping=project_mapping)

    # Sprawdzenie, czy dane zostały poprawnie wprowadzone (bez relacji)
    print("Dane w tabeli 'Department' (bez relacji):")
    display_model_data_as_dataframe(Department, exclude_relations=True)

    print("Dane w tabeli 'Project' (bez relacji):")
    display_model_data_as_dataframe(Project, exclude_relations=True)

    # Wyczyść i wypełnij tabelę EmployeeAssignment, resetując indeksy
    populate_table(EmployeeAssignment, df_employee_assignments, clear=True, column_mapping=employee_assignment_mapping)

    # Wyświetl dane z tabeli EmployeeAssignment
    print("Dane w tabeli 'EmployeeAssignment':")
    display_model_data_as_dataframe(EmployeeAssignment)
