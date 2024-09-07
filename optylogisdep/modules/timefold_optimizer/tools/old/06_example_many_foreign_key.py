import os
import pandas as pd
from django.apps import apps
from data_utils import process_data, display_model_data_as_dataframe

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django
django.setup()

# Przykład użycia
if __name__ == "__main__":
    # Pobranie modeli Django
    Department = apps.get_model('optylogis', 'Department')
    Project = apps.get_model('optylogis', 'Project')
    EmployeeAssignment = apps.get_model('optylogis', 'EmployeeAssignment')

    # Dane do tabel
    data_departments = {
        'name': ['HR', 'Finance', 'Engineering'],
        'description': ['Human Resources', 'Financial Department', 'Engineering Department']
    }

    data_projects = {
        'name': ['Project X', 'Project Y', 'Project Z'],
        'description': ['Top Secret Project X', 'Top Secret Project Y', 'Top Secret Project Z']
    }

    data_employee_assignments = {
        'department': ['Finance', 'Finance', 'HR'],
        'proj': ['Project X', 'Project X', 'Project Miss'],  # Zaktualizowane nazwy kolumn
        'role': ['Manager', 'Analyst', 'Recruiter'],
        'proj_description': ['Lead', 'Support', 'Lead']
    }

    # Tworzenie DataFrame'ów
    df_departments = pd.DataFrame(data_departments)
    df_projects = pd.DataFrame(data_projects)
    df_employee_assignments = pd.DataFrame(data_employee_assignments)

    # Wypełnianie tabel
    print("Wypełnianie tabeli 'Department'")
    process_data(df_departments, model=Department)

    print("Wypełnianie tabeli 'Project'")
    process_data(df_projects, model=Project)

    print("Sprawdzenie danych w tabelach 'Department' i 'Project' (bez relacji)")
    print("Dane w tabeli 'Department':")
    display_model_data_as_dataframe(Department, exclude_relations=True)

    print("Dane w tabeli 'Project':")
    display_model_data_as_dataframe(Project, exclude_relations=True)

    print("Wypełnianie tabeli 'EmployeeAssignment'")
    process_data(df_employee_assignments, df_ref=df_projects, model=EmployeeAssignment,
                 foreign_keys={'department': (Department, 'name'), 'proj': (Project, 'name')}, key='proj')

    # Wyświetl dane z tabeli EmployeeAssignment
    print("Dane w tabeli 'EmployeeAssignment':")
    display_model_data_as_dataframe(EmployeeAssignment)
