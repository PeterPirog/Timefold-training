import os

import pandas as pd
from django.apps import apps
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django
django.setup()

def clear_and_reset_table(Model):
    """
    Usuwa wszystkie dane z tabeli modelu Django i resetuje sekwencję klucza głównego.

    Args:
        Model (models.Model): Model Django dla tabeli, którą chcesz wyczyścić i zresetować indeksy.
    """
    Model.objects.all().delete()
    with connection.cursor() as cursor:
        table_name = Model._meta.db_table
        if connection.vendor == 'postgresql':
            cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;")
        elif connection.vendor == 'sqlite':
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}';")
        else:
            print(f"Manual sequence reset might be required for your database: {connection.vendor}")
    print(f"Cleared and reset index for table: {Model.__name__}")

def get_related_instance(field, value):
    """
    Pobiera instancję powiązanego modelu na podstawie klucza obcego.

    Args:
        field (models.Field): Pole modelu Django będące kluczem obcym.
        value (str): Wartość identyfikująca rekord w powiązanej tabeli.

    Returns:
        models.Model: Instancja powiązanego modelu.
    """
    related_model = field.related_model
    try:
        return related_model.objects.get(name=value)
    except related_model.DoesNotExist:
        print(f"Error: No {related_model.__name__} found with name='{value}'")
        raise

def prepare_instance_data(Model, row, column_mapping=None):
    """
    Przygotowuje dane do utworzenia lub aktualizacji instancji modelu Django.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być przygotowane.
        row (pd.Series): Wiersz danych z DataFrame.
        column_mapping (dict): Opcjonalny słownik mapujący nazwy kolumn w DataFrame na nazwy pól w Django modelu.

    Returns:
        dict: Słownik danych do stworzenia lub aktualizacji instancji modelu.
    """
    instance_data = {}
    for field in Model._meta.get_fields():
        if column_mapping and field.name in column_mapping.values():
            df_column = [key for key, value in column_mapping.items() if value == field.name][0]
        else:
            df_column = field.name

        if field.is_relation and field.many_to_one:
            instance_data[field.name] = get_related_instance(field, row[df_column])
        elif df_column in row:
            instance_data[field.name] = row[df_column]
    return instance_data

def populate_table(Model, df_data, clear=False, column_mapping=None):
    """
    Zapisuje dane z DataFrame do tabeli modelu Django, obsługując klucze obce.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być zapisane.
        df_data (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli modelu.
        clear (bool): Flaga określająca, czy usunąć wszystkie dane z tabeli przed zapisaniem nowych.
        column_mapping (dict): Opcjonalny słownik mapujący nazwy kolumn w DataFrame na nazwy pól w Django modelu.
    """
    if clear:
        clear_and_reset_table(Model)
        df_data.reset_index(drop=True, inplace=True)  # Resetowanie indeksów w DataFrame

    instances = []
    for _, row in df_data.iterrows():
        instance_data = prepare_instance_data(Model, row, column_mapping)
        instances.append(Model(**instance_data))

    Model.objects.bulk_create(instances, ignore_conflicts=True)

def display_model_data_as_dataframe(Model, exclude_relations=False):
    """
    Wyświetla dane z dowolnego modelu Django w formacie Pandas DataFrame,
    uwzględniając zarówno klucze obce, jak i zwykłe pola.

    Args:
        Model (models.Model): Model Django, którego dane mają zostać wyświetlone.
        exclude_relations (bool): Flaga określająca, czy wykluczyć pola związane z relacjami.
    """
    instances = Model.objects.all() if exclude_relations else Model.objects.select_related()
    data = []

    for instance in instances:
        row = {}
        for field in Model._meta.get_fields():
            if exclude_relations and (field.is_relation or field.many_to_one):
                continue
            if field.is_relation and field.many_to_one:
                related_object = getattr(instance, field.name)
                row[field.name] = getattr(related_object, 'name', related_object.pk) if related_object else None
            else:
                row[field.name] = getattr(instance, field.name)
        data.append(row)

    df = pd.DataFrame(data)
    df.reset_index(drop=True, inplace=True)  # Resetowanie indeksów w DataFrame przed wyświetleniem
    print(df)

# Przykład użycia
if __name__ == "__main__":
    Department = apps.get_model('optylogis', 'Department')
    Project = apps.get_model('optylogis', 'Project')
    EmployeeAssignment = apps.get_model('optylogis', 'EmployeeAssignment')

    data_department = {
        'dept_name': ['HR', 'IT', 'Finance'],
        'description': ['Human Resources', 'Information Technology', 'Financial Department']
    }

    df_department = pd.DataFrame(data_department)

    data_employee_assignment = {
        'dept': ['HR', 'IT', 'HR'],
        'proj': ['Project A', 'Project B', 'Project C'],
        'role': ['Manager', 'Developer', 'Analyst'],
    }

    df_employee_assignment = pd.DataFrame(data_employee_assignment)

    # Mapowanie kolumn DataFrame na pola Django modelu
    department_mapping = {
        'dept_name': 'name',
        'description': 'description'
    }

    project_mapping = {
        'proj_name': 'name',
        'description': 'description'
    }

    employee_assignment_mapping = {
        'dept': 'department',
        'proj': 'project',
        'role': 'role'
    }

    # Wyczyść i wypełnij tabelę Department, Project, oraz EmployeeAssignment, resetując indeksy
    populate_table(Department, df_department, clear=True, column_mapping=department_mapping)

    # Sprawdzenie, czy dane zostały poprawnie wprowadzone (bez relacji)
    print("Dane w tabeli 'Department' (bez relacji):")
    display_model_data_as_dataframe(Department, exclude_relations=True)

    populate_table(Project, df_employee_assignment, clear=True, column_mapping=employee_assignment_mapping)

    # Wyświetl dane z tabeli EmployeeAssignment
    print("Dane w tabeli 'EmployeeAssignment':")
    display_model_data_as_dataframe(EmployeeAssignment)
