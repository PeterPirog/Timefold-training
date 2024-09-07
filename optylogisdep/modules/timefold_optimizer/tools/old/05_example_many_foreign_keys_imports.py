import os

import pandas as pd
from django.apps import apps

from data_utils import populate_table, display_model_data_as_dataframe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django

django.setup()

# Przykład użycia
if __name__ == "__main__":
    Department = apps.get_model('optylogis', 'Department')
    Project = apps.get_model('optylogis', 'Project')
    EmployeeAssignment = apps.get_model('optylogis', 'EmployeeAssignment')

    data_department = {
        'dept_name': ['HR', 'IT', 'Finance'],
        'description': ['Human Resources', 'Information Technology', 'Financial Department']
    }

    data_project = {
        'name': ['Project Alpha', 'Project Beta', 'Project Gamma'],
        'description': ['Alpha Project Description', 'Beta Project Description', 'Gamma Project Description']
    }

    data_employee_assignment = {
        'dept': ['HR', 'IT', 'Finance'],
        'proj': ['Project Alpha', 'Project Beta', 'Project Miss'],
        # 'Project Miss' value doesn't exist in Project table
        'role': ['Manager', 'Developer', 'Analyst'],
        'proj_description': ['Lead Alpha', 'Develop Beta', 'Analyze Gamma']
    }

    df_department = pd.DataFrame(data_department)
    df_project = pd.DataFrame(data_project)
    df_employee_assignment = pd.DataFrame(data_employee_assignment)

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

    # Wyczyść i wypełnij tabelę Department i Project, resetując indeksy
    populate_table(Department, df_department, clear=True, column_mapping=department_mapping)
    populate_table(Project, df_project, clear=True, column_mapping=project_mapping)

    # Sprawdzenie, czy dane zostały poprawnie wprowadzone (bez relacji)
    print("Dane w tabeli 'Department' (bez relacji):")
    display_model_data_as_dataframe(Department, exclude_relations=True)

    print("Dane w tabeli 'Project' (bez relacji):")
    display_model_data_as_dataframe(Project, exclude_relations=True)

    # Wyczyść i wypełnij tabelę EmployeeAssignment, resetując indeksy
    populate_table(EmployeeAssignment, df_employee_assignment, clear=True, column_mapping=employee_assignment_mapping)

    # Wyświetl dane z tabeli EmployeeAssignment
    print("Dane w tabeli 'EmployeeAssignment':")
    display_model_data_as_dataframe(EmployeeAssignment)
