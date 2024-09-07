import pandas as pd
import os
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django
django.setup()

def clear_table(Model):
    """
    Usuwa wszystkie dane z tabeli modelu Django.

    Args:
        Model (models.Model): Model Django dla tabeli, którą chcesz wyczyścić.
    """
    Model.objects.all().delete()

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
    return related_model.objects.get(name=value)

def prepare_instance_data(Model, row):
    """
    Przygotowuje dane do utworzenia lub aktualizacji instancji modelu Django.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być przygotowane.
        row (pd.Series): Wiersz danych z DataFrame.

    Returns:
        dict: Słownik danych do stworzenia lub aktualizacji instancji modelu.
    """
    instance_data = {}
    for field in Model._meta.get_fields():
        if field.is_relation and field.many_to_one:
            instance_data[field.name] = get_related_instance(field, row[field.name])
        elif field.name in row:
            instance_data[field.name] = row[field.name]
    return instance_data

def populate_table(Model, df_data, clear=False):
    """
    Zapisuje dane z DataFrame do tabeli modelu Django, obsługując klucze obce.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być zapisane.
        df_data (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli modelu.
        clear (bool): Flaga określająca, czy usunąć wszystkie dane z tabeli przed zapisaniem nowych.
    """
    if clear:
        clear_table(Model)
        df_data.reset_index(drop=True, inplace=True)  # Resetowanie indeksów w DataFrame

    instances = []
    for _, row in df_data.iterrows():
        instance_data = prepare_instance_data(Model, row)
        instances.append(Model(**instance_data))

    Model.objects.bulk_create(instances, ignore_conflicts=True)

def display_model_data_as_dataframe(Model):
    """
    Wyświetla dane z dowolnego modelu Django w formacie Pandas DataFrame,
    uwzględniając zarówno klucze obce, jak i zwykłe pola.

    Args:
        Model (models.Model): Model Django, którego dane mają zostać wyświetlone.
    """
    instances = Model.objects.select_related()
    data = []

    for instance in instances:
        row = {}
        for field in Model._meta.get_fields():
            if field.is_relation and field.many_to_one:
                related_object = getattr(instance, field.name)
                row[field.name] = getattr(related_object, 'name', related_object.pk) if related_object else None
            else:
                row[field.name] = getattr(instance, field.name)
        data.append(row)

    df = pd.DataFrame(data)
    print(df)

# Przykład użycia
if __name__ == "__main__":

    Context = apps.get_model('optylogis', 'Context')
    Relationship = apps.get_model('optylogis', 'Relationship')

    data_context = {
        'name': ['Context A', 'Context B', 'Context C'],
        'description': ['Description for A', 'Description for B', 'Description for C']
    }

    df_context = pd.DataFrame(data_context)

    data_relationship = {
        'context1': ['Context B', 'Context B', 'Context A'],
        'context2': ['Context A', 'Context A', 'Context C'],
        'context3': ['C1', 'C2', 'C3']
    }

    df_relationship = pd.DataFrame(data_relationship)

    # Wyczyść i wypełnij tabelę Context, resetując indeksy
    populate_table(Context, df_context, clear=True)

    # Wyczyść i wypełnij tabelę Relationship, resetując indeksy
    populate_table(Relationship, df_relationship, clear=True)

    # Wyświetl dane z tabeli Relationship
    display_model_data_as_dataframe(Relationship)
