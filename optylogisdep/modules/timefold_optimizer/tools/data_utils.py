import pandas as pd
from django.db import connection, models


def clear_and_reset_table(Model: models.Model) -> None:
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
    print(f"Cleared and reset index for table: {Model.__name__}\n")


from typing import Optional, Dict, Any
from django.db import models


def get_related_instance(field: models.Field, value: str, row_info: Dict[str, Any]) -> Optional[models.Model]:
    """
    Pobiera instancję powiązanego modelu na podstawie klucza obcego.

    Args:
        field (models.Field): Pole modelu Django będące kluczem obcym.
        value (str): Wartość identyfikująca rekord w powiązanej tabeli.
        row_info (dict): Słownik zawierający pełne informacje o wierszu, używany do wyświetlania w razie braku dopasowania.

    Returns:
        Optional[models.Model]: Instancja powiązanego modelu lub None, jeśli rekord nie zostanie znaleziony.
    """
    related_model = field.related_model
    try:
        return related_model.objects.get(name=value)
    except related_model.DoesNotExist:
        print(f"Warning: No {related_model.__name__} found with name='{value}'. Skipping this record: {row_info}")
        return None


def prepare_instance_data(
        Model: models.Model,
        row: pd.Series,
        row_info: Dict[str, Any],
        column_mapping: Optional[Dict[str, str]] = None
) -> Optional[Dict[str, Any]]:
    """
    Przygotowuje dane do utworzenia lub aktualizacji instancji modelu Django.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być przygotowane.
        row (pd.Series): Wiersz danych z DataFrame.
        row_info (dict): Pełne informacje o wierszu, używane w przypadku błędu.
        column_mapping (dict, optional): Opcjonalny słownik mapujący nazwy kolumn w DataFrame na nazwy pól w Django modelu.

    Returns:
        Optional[Dict[str, Any]]: Słownik danych do stworzenia lub aktualizacji instancji modelu, lub None, jeśli nie można przygotować danych.
    """
    instance_data = {}
    for field in Model._meta.get_fields():
        if column_mapping and field.name in column_mapping.values():
            df_column = next(key for key, value in column_mapping.items() if value == field.name)
        else:
            df_column = field.name

        if field.is_relation and field.many_to_one:
            related_instance = get_related_instance(field, row[df_column], row_info)
            if related_instance is None:
                return None
            instance_data[field.name] = related_instance
        elif df_column in row:
            instance_data[field.name] = row[df_column]
    return instance_data


def populate_table(
        Model: models.Model,
        df_data: pd.DataFrame,
        clear: bool = False,
        column_mapping: Optional[Dict[str, str]] = None
) -> None:
    """
    Zapisuje dane z DataFrame do tabeli modelu Django, obsługując klucze obce.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być zapisane.
        df_data (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli modelu.
        clear (bool, optional): Flaga określająca, czy usunąć wszystkie dane z tabeli przed zapisaniem nowych. Domyślnie False.
        column_mapping (dict, optional): Opcjonalny słownik mapujący nazwy kolumn w DataFrame na nazwy pól w Django modelu.
    """
    if clear:
        clear_and_reset_table(Model)
        df_data.reset_index(drop=True, inplace=True)

    instances = []
    for _, row in df_data.iterrows():
        row_info = row.to_dict()  # Zbieramy informacje o całym wierszu
        instance_data = prepare_instance_data(Model, row, row_info, column_mapping)
        if instance_data is not None:
            instances.append(Model(**instance_data))

    Model.objects.bulk_create(instances, ignore_conflicts=True)


def display_model_data_as_dataframe(Model: models.Model, exclude_relations: bool = False) -> None:
    """
    Wyświetla dane z dowolnego modelu Django w formacie Pandas DataFrame,
    uwzględniając zarówno klucze obce, jak i zwykłe pola.

    Args:
        Model (models.Model): Model Django, którego dane mają zostać wyświetlone.
        exclude_relations (bool, optional): Flaga określająca, czy wykluczyć pola związane z relacjami. Domyślnie False.
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
    df.reset_index(drop=True, inplace=True)
    print(df)
    print("\n")  # Dodaj pustą linię po każdej tabeli dla lepszej czytelności
