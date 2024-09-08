import pandas as pd
from django.db import models
from django.db.models.functions import Length
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




def update_indexy_4_updated(Indexy_4, Indexy_4_updated, Ind4_om):
    """
    Funkcja aktualizująca dane w tabeli Indexy_4_updated na podstawie tabeli Indexy_4 i Ind4_om.

    Args:
        Indexy_4: Model tabeli Indexy_4
        Indexy_4_updated: Model tabeli Indexy_4_updated
        Ind4_om: Model tabeli Ind4_om
    """
    # Usuń wszystkie rekordy z Indexy_4_updated, aby upewnić się, że jest pusta
    Indexy_4_updated.objects.all().delete()

    # Skopiuj wszystkie dane z Indexy_4 do Indexy_4_updated za pomocą bulk_create
    indexy_4_records = Indexy_4.objects.all()

    # Tworzenie listy obiektów Indexy_4_updated
    updated_records = [
        Indexy_4_updated(
            indeks=record.indeks,
            nazwa=record.nazwa,
            nsn=record.nsn,
            p_jm=record.p_jm,
            p_prod=record.p_prod,
            p_komplet=record.p_komplet,
            p_tech=record.p_tech,
            p_wymagani=record.p_wymagani,
            ind_rek=record.ind_rek,
            p_pwaz_k=record.p_pwaz_k,
            p_pwaz_u=record.p_pwaz_u,
            p_norma_k=record.p_norma_k,
            p_norma_u=record.p_norma_u,
        )
        for record in indexy_4_records
    ]

    # Użycie bulk_create do wstawienia wszystkich rekordów za jednym razem
    Indexy_4_updated.objects.bulk_create(updated_records)

    # Usunięcie filtrowania po długości indeksu, aby nie pomijać rekordów
    indexy_4_updated_records = Indexy_4_updated.objects.all()

    # Licznik zaktualizowanych rekordów
    updated_count = 0

    # Iteracja przez wszystkie rekordy w Indexy_4_updated
    for record in indexy_4_updated_records:
        try:
            # Szukamy odpowiedniego rekordu w Ind4_om na podstawie pola 'indeks'
            ind4_om_record = Ind4_om.objects.get(indeks=record.indeks)

            # Aktualizujemy pola w Indexy_4_updated na podstawie rekordu z Ind4_om
            record.p_pwaz_k = ind4_om_record.p_pwaz_k
            record.p_pwaz_u = ind4_om_record.p_pwaz_u
            record.p_norma_k = ind4_om_record.p_norma_k
            record.p_norma_u = ind4_om_record.p_norma_u

            # Zapisujemy zaktualizowany rekord
            record.save()

            # Zwiększamy licznik zaktualizowanych rekordów
            updated_count += 1

        except Ind4_om.DoesNotExist:
            pass

    print(f"Aktualizacja zakończona. Zaktualizowano {updated_count} rekordów.")

    return indexy_4_updated_records

def compare_and_remove_missing(table_to_clean, table_to_check, field_to_clean, field_to_check):
    """
    Funkcja porównująca rekordy między dwiema tabelami, aby znaleźć rekordy w `table_to_clean`,
    które nie mają odpowiednika w `table_to_check`, oraz usuwa te rekordy.

    Args:
        table_to_clean: Model tabeli, która ma być "czyszczona" (z której rekordy zostaną usunięte)
        table_to_check: Model tabeli, w której szukamy brakujących rekordów
        field_to_clean: Nazwa pola w `table_to_clean`, które chcemy porównać
        field_to_check: Nazwa pola w `table_to_check`, względem którego porównujemy

    Returns:
        None: Wyświetla różnice w konsoli i usuwa brakujące rekordy z `table_to_clean`
    """
    # Pobierz wartości z tabeli do porównania
    check_values = table_to_check.objects.values_list(field_to_check, flat=True)

    # Znajdź rekordy w table_to_clean, które nie mają odpowiednika w table_to_check
    missing_records = table_to_clean.objects.exclude(**{f"{field_to_clean}__in": check_values})

    # Konwertuj wyniki do pandas DataFrame
    df_missing = pd.DataFrame.from_records(missing_records.values())

    if df_missing.empty:
        print(f"Wszystkie rekordy w {table_to_clean._meta.db_table} mają odpowiednik w {table_to_check._meta.db_table}.")
    else:
        print(f"Znaleziono {len(df_missing)} rekordów w {table_to_clean._meta.db_table}, które nie występują w {table_to_check._meta.db_table}:")
        print(df_missing)

        # Usunięcie brakujących rekordów z bazy danych
        missing_count, _ = missing_records.delete()
        print(f"Usunięto {missing_count} rekordów z tabeli {table_to_clean._meta.db_table}.")