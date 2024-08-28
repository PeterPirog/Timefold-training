import pandas as pd
import os
from django.db import connection
from django.apps import apps

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

    Context = apps.get_model('optylogis', 'Context')
    Relationship = apps.get_model('optylogis', 'Relationship')

    data_context = {
        'ctx_name': ['Context A', 'Context B', 'Context C'],
        'description': ['Description for A', 'Description for B', 'Description for C']
    }

    df_context = pd.DataFrame(data_context)

    data_relationship = {
        'ctx1': ['Context B', 'Context B', 'Context A'],
        'ctx2': ['Context A', 'Context A', 'Context C'],
        'ctx3': ['C1', 'C2', 'C3']
    }

    df_relationship = pd.DataFrame(data_relationship)

    # Mapowanie kolumn DataFrame na pola Django modelu
    context_mapping = {
        'ctx_name': 'name',
        'description': 'description'
    }

    relationship_mapping = {
        'ctx1': 'context1',
        'ctx2': 'context2',
        'ctx3': 'context3'
    }

    # Wyczyść i wypełnij tabelę Context, resetując indeksy
    populate_table(Context, df_context, clear=True, column_mapping=context_mapping)

    # Sprawdzenie, czy dane zostały poprawnie wprowadzone (bez relacji)
    print("Dane w tabeli 'Context' (bez relacji):")
    display_model_data_as_dataframe(Context, exclude_relations=True)

    # Wyczyść i wypełnij tabelę Relationship, resetując indeksy
    populate_table(Relationship, df_relationship, clear=True, column_mapping=relationship_mapping)

    # Wyświetl dane z tabeli Relationship
    display_model_data_as_dataframe(Relationship)
