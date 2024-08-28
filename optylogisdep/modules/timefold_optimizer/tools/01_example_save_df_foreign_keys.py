import pandas as pd
import os
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django
django.setup()
from optylogis.models import Context, Relationship

def reset_primary_key_table(Model):
    """
    Usuwa tabelę i tworzy ją ponownie.

    Args:
        Model (models.Model): Model Django dla tabeli, którą chcesz zresetować.
    """
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(Model)
        schema_editor.create_model(Model)

def populate_model_table(Model, df_data, reset=False, reset_related_models=None):
    """
    Zapisuje dane z DataFrame do tabeli modelu Django, z opcjonalnym usunięciem wszystkich danych i zresetowaniem tabeli.
    Obsługuje również klucze obce.

    Args:
        Model (models.Model): Model Django, dla którego dane mają być zapisane.
        df_data (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli modelu.
        reset (bool): Flaga określająca, czy usunąć wszystkie dane z tabeli i ponownie ją utworzyć.
        reset_related_models (list): Lista modeli Django, które powinny zostać zresetowane przed zresetowaniem głównego modelu.
    """
    if reset:
        if reset_related_models:
            for related_model in reset_related_models:
                reset_primary_key_table(related_model)  # Usuwamy zależne tabele
        reset_primary_key_table(Model)
        df_data.reset_index(drop=True, inplace=True)

    for _, row in df_data.iterrows():
        defaults = {}
        unique_fields = {}

        for field in Model._meta.fields:
            if field.name in df_data.columns:
                if field.is_relation and field.many_to_one:  # Obsługa kluczy obcych
                    related_model = getattr(Model, field.name).field.related_model
                    related_instance = related_model.objects.get(**{field.related_model._meta.pk.name: row[field.name]})
                    defaults[field.name] = related_instance
                else:
                    defaults[field.name] = row[field.name]

                if field.unique:
                    unique_fields[field.name] = row[field.name]

        if not unique_fields:
            # Sprawdź, czy 'id' istnieje w df_data, jeśli nie, użyj innego pola
            if Model._meta.pk.name in df_data.columns:
                unique_fields = {Model._meta.pk.name: row[Model._meta.pk.name]}
            else:
                # W przypadku braku unikalnych pól w DataFrame, możemy podjąć inną akcję
                # Na przykład użyć 'name' lub innego pola, które powinno być unikalne
                if 'name' in df_data.columns:
                    unique_fields = {'name': row['name']}
                else:
                    raise ValueError("Nie znaleziono unikalnego pola do identyfikacji rekordu.")

        Model.objects.update_or_create(
            defaults=defaults,
            **unique_fields
        )

def populate_foreign_key_table(Relationship, df_relationship):
    """
    Zapisuje dane z DataFrame do tabeli z kluczem obcym, obsługując duplikaty kluczy.
    Automatycznie pobiera klucze obce i tworzy powiązane instancje.

    Args:
        Relationship (models.Model): Model Django dla tabeli 'Relationship'.
        df_relationship (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli z kluczem obcym.
    """
    relationship_instances = []

    for _, row in df_relationship.iterrows():
        instance_data = {}

        # Przejdź przez wszystkie pola modelu Relationship
        for field in Relationship._meta.get_fields():
            if field.is_relation and field.many_to_one:  # Sprawdź, czy pole jest kluczem obcym
                related_model = field.related_model  # Pobierz model powiązany
                related_instance = related_model.objects.get(name=row[field.name])  # Pobierz instancję powiązanego modelu na podstawie nazwy
                instance_data[field.name] = related_instance
            elif field.name in df_relationship.columns:  # Dla pól, które nie są kluczami obcymi
                instance_data[field.name] = row[field.name]

        # Tworzenie instancji Relationship z dynamicznie pobranymi danymi
        relationship_instances.append(Relationship(**instance_data))

    # Bulk create, ignorując konflikty
    Relationship.objects.bulk_create(relationship_instances, ignore_conflicts=True)



def display_model_data_as_dataframe(Model):
    """
    Wyświetla dane z dowolnego modelu Django w formacie Pandas DataFrame,
    uwzględniając zarówno klucze obce, jak i zwykłe pola.

    Args:
        Model (models.Model): Model Django, którego dane mają zostać wyświetlone.
    """
    # Pobierz wszystkie instancje modelu z powiązanymi obiektami kluczy obcych
    instances = Model.objects.select_related()

    data = []
    for instance in instances:
        row = {}
        for field in Model._meta.get_fields():
            if field.is_relation and field.many_to_one:  # Sprawdź, czy pole jest kluczem obcym
                related_object = getattr(instance, field.name)
                if related_object:
                    # Dodaj nazwę powiązanego obiektu (zwykle pole 'name', ale można to dostosować)
                    row[field.name] = getattr(related_object, 'name', related_object.pk)
                else:
                    row[field.name] = None
            else:
                # Dodaj zwykłe pole
                row[field.name] = getattr(instance, field.name)
        data.append(row)

    # Konwersja danych do DataFrame
    df = pd.DataFrame(data)
    print(df)

# Przykład użycia
if __name__ == "__main__":

    data_context = {
        'name': ['Context A', 'Context B', 'Context C'],
        'description': ['Description for A', 'Description for B', 'Description for C']
    }

    df_context = pd.DataFrame(data_context)

    data_relationship = {
        'context1': ['Context B', 'Context B', 'Context A'],
        'context2': ['Context A', 'Context A', 'Context C'],
        'context3': ['C1', 'C2', 'C3']  # Assuming 'context3' is a regular field, not a ForeignKey
    }

    df_relationship = pd.DataFrame(data_relationship)

    # Zresetuj i wypełnij tabelę Context oraz zresetuj indeksy
    reset_primary_key_table(Relationship)  # Zresetuj najpierw zależną tabelę
    reset_primary_key_table(Context)  # Następnie zresetuj tabelę główną

    # Zapisz dane do tabeli Context
    populate_model_table(Context, df_context, reset=False)

    # Zapisz dane do tabeli Relationship
    populate_foreign_key_table(Relationship, df_relationship)

    # Wyświetl dane z tabeli Relationship
    display_model_data_as_dataframe(Relationship)
