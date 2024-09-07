import pandas as pd
from django.db import models
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from tablib import Dataset

def get_model_fields(model):
    """
    Pobiera listę wszystkich pól w modelu Django.

    Args:
        model: Model Django.

    Returns:
        Listę nazw pól modelu.
    """
    return [field.name for field in model._meta.fields]

def get_unique_field(model):
    """
    Zwraca nazwę unikalnego pola modelu (np. 'l_pesel' lub inne unikalne pole).

    Args:
        model: Model Django.

    Returns:
        Nazwa unikalnego pola.
    """
    unique_fields = [field.name for field in model._meta.fields if field.unique and field.name != 'id']
    if unique_fields:
        return unique_fields[0]  # Zwróć pierwszy unikalny identyfikator
    return 'id'

def create_resource_class(model, foreign_keys=None):
    """
    Tworzy dynamicznie klasę zasobu dla podanego modelu Django.

    Args:
        model: Model Django, dla którego tworzona jest klasa zasobu.
        foreign_keys: Słownik z nazwami pól kluczy obcych i modelami powiązanymi.

    Returns:
        Dynamicznie utworzona klasa zasobu.
    """
    model_ref = model
    unique_field = get_unique_field(model_ref)

    class Meta:
        model = model_ref
        fields = get_model_fields(model_ref)
        if unique_field != 'id':
            import_id_fields = (unique_field,)

    attrs = {'Meta': Meta}

    if foreign_keys:
        for field_name, (related_model, related_field) in foreign_keys.items():
            attrs[field_name] = fields.Field(
                column_name=field_name,
                attribute=field_name,
                widget=ForeignKeyWidget(related_model, related_field)
            )

    resource_class = type(f'{model.__name__}Resource', (resources.ModelResource,), attrs)
    return resource_class

def verify_and_remove_missing_foreign_keys(df, df_ref, key, key_name, on_delete_behavior):
    """
    Sprawdza brakujące klucze obce w dataframe i usuwa lub ustawia na NULL niepasujące rekordy
    w zależności od zdefiniowanego zachowania on_delete.

    Args:
        df: Główna tabela DataFrame.
        df_ref: Tabela referencyjna DataFrame z wartościami kluczy obcych.
        key: Nazwa kolumny klucza obcego w df.
        key_name: Nazwa kolumny klucza obcego w df_ref.
        on_delete_behavior: Zachowanie on_delete (CASCADE lub SET_NULL).

    Returns:
        Zaktualizowany DataFrame bez brakujących kluczy obcych.
    """
    missing_keys = df[~df[key].isin(df_ref[key_name])]
    if not missing_keys.empty:
        print(f"Brakujące rekordy {key} w źródłowym dataframe:")
        print(missing_keys)
        if on_delete_behavior == 'CASCADE':
            df = df[df[key].isin(df_ref[key_name])]
        elif on_delete_behavior == 'SET_NULL':
            df.loc[~df[key].isin(df_ref[key_name]), key] = None
    return df

def load_data(resource_class, df):
    """
    Ładuje dane z DataFrame do modelu Django za pomocą zasobu.

    Args:
        resource_class: Klasa zasobu do importu danych.
        df: DataFrame do zaimportowania.

    Returns:
        Wynik importu.
    """
    resource = resource_class()
    dataset = Dataset().load(df.to_csv(index=False), format='csv')
    result = resource.import_data(dataset, raise_errors=True, dry_run=False)
    return result

def process_data(df, df_ref_dict=None, model=None, foreign_keys=None):
    """
    Procesuje dane z uwzględnieniem kluczy obcych i importuje je do modelu Django.

    Args:
        df: Główna tabela DataFrame.
        df_ref_dict: Słownik zawierający DataFrame'y referencyjne dla kluczy obcych.
        model: Model Django, do którego dane będą importowane.
        foreign_keys: Słownik z nazwami pól kluczy obcych i modelami powiązanymi.

    Returns:
        Wynik importu.
    """
    if foreign_keys and df_ref_dict:
        for fk_field, (related_model, related_field) in foreign_keys.items():
            df_ref = df_ref_dict[related_model]

            # Sprawdzenie, które rekordy mają brakujące klucze obce lub niewłaściwe wartości, np. '#######'
            missing_keys = df[~df[fk_field].isin(df_ref[related_field]) | df[fk_field].isin(['#######'])]
            if not missing_keys.empty:
                # Jeśli klucz obcy ma on_delete ustawione na CASCADE, pomiń rekord
                if model._meta.get_field(fk_field).remote_field.on_delete.__name__ == 'CASCADE':
                    print(f"Rekordy z brakującymi lub niewłaściwymi kluczami obcymi dla {fk_field} w modelu {model.__name__} zostaną pominięte:")
                    print(missing_keys)
                    df = df[df[fk_field].isin(df_ref[related_field]) & ~df[fk_field].isin(['#######'])]
                # Jeśli klucz obcy ma on_delete ustawione na SET_NULL, ustaw wartość NULL
                elif model._meta.get_field(fk_field).remote_field.on_delete.__name__ == 'SET_NULL':
                    print(f"Rekordy z brakującymi lub niewłaściwymi kluczami obcymi dla {fk_field} w modelu {model.__name__} będą miały wartość {fk_field} ustawioną na NULL:")
                    print(missing_keys)
                    df.loc[~df[fk_field].isin(df_ref[related_field]) | df[fk_field].isin(['#######']), fk_field] = None

    resource_class = create_resource_class(model, foreign_keys)
    result = load_data(resource_class, df)
    return result


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
                row[field.name] = getattr(related_object, get_unique_field(field.related_model), related_object.pk) if related_object else None
            else:
                row[field.name] = getattr(instance, field.name)
        data.append(row)

    df = pd.DataFrame(data)
    df.reset_index(drop=True, inplace=True)
    print(df)
    print("\n")  # Dodaj pustą linię po każdej tabeli dla lepszej czytelności

def queryset_to_dataframe(queryset):
    """
    Konwertuje Django QuerySet na pandas DataFrame.

    Args:
    queryset: Django QuerySet, który chcemy przekonwertować

    Returns:
    pandas.DataFrame: DataFrame zawierający dane z QuerySet
    """
    # Konwersja QuerySet do listy słowników
    records_list = list(queryset.values())

    # Konwersja listy słowników na DataFrame
    if records_list:
        df = pd.DataFrame(records_list)
    else:
        # Jeśli QuerySet jest pusty, zwróć pusty DataFrame
        df = pd.DataFrame()

    return df