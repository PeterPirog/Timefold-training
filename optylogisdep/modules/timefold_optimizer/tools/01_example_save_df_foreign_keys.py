import pandas as pd
import os
from django.core.exceptions import MultipleObjectsReturned
from django.db import connection

# Ustawienie zmiennej środiskowej dla Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

# Importowanie Django i ustawienie środowiska Django
import django
django.setup()

def reset_relationship_table(Context, Relationship):
    """
    Usuwa tabelę 'Relationship' i tworzy ją ponownie.

    Args:
        Context (models.Model): Model Django dla tabeli 'Context'.
        Relationship (models.Model): Model Django dla tabeli 'Relationship'.
    """
    with connection.schema_editor() as schema_editor:
        schema_editor.delete_model(Relationship)  # Usunięcie tabeli Relationship
        schema_editor.create_model(Relationship)  # Ponowne stworzenie tabeli Relationship

def reset_context_table(Context, reset=False):
    """
    Usuwa tabelę 'Context' i tworzy ją ponownie, jeśli reset jest włączony.

    Args:
        Context (models.Model): Model Django dla tabeli 'Context'.
        reset (bool): Flaga określająca, czy resetować tabelę 'Context'.
    """
    if reset:
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(Context)  # Usunięcie tabeli Context
            schema_editor.create_model(Context)  # Ponowne stworzenie tabeli Context

def populate_context_table(Context, df_context):
    """
    Zapisuje dane z DataFrame do tabeli 'Context'.

    Args:
        Context (models.Model): Model Django dla tabeli 'Context'.
        df_context (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli 'Context'.
    """
    for _, row in df_context.iterrows():
        context, created = Context.objects.get_or_create(name=row['name'], defaults={'description': row['description']})
        if not created:
            context.description = row['description']
            context.save()

def populate_relationship_table(Context, Relationship, df_relationship):
    """
    Zapisuje dane z DataFrame do tabeli 'Relationship', obsługując duplikaty kluczy.

    Args:
        Context (models.Model): Model Django dla tabeli 'Context'.
        Relationship (models.Model): Model Django dla tabeli 'Relationship'.
        df_relationship (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli 'Relationship'.
    """
    for _, row in df_relationship.iterrows():
        try:
            # Znajdź odpowiednie obiekty Context na podstawie pola 'name' używając get
            context1 = Context.objects.get(name=row['context1_name'])
            context2 = Context.objects.get(name=row['context2_name'])

            # Utwórz i zapisz obiekt Relationship
            relationship = Relationship(context1=context1, context2=context2)
            relationship.save()

        except MultipleObjectsReturned:
            print(f"Multiple objects returned for context1_name='{row['context1_name']}' or context2_name='{row['context2_name']}'.")
            # Możesz tutaj zadecydować, co zrobić w przypadku duplikatów

def fetch_relationship_data(Relationship):
    """
    Pobiera dane z tabeli 'Relationship' i drukuje powiązane wartości z tabeli 'Context'.

    Args:
        Relationship (models.Model): Model Django dla tabeli 'Relationship'.
    """
    relationships = Relationship.objects.select_related('context1', 'context2')
    for relationship in relationships:
        print(f"Context1: {relationship.context1.name}, Context2: {relationship.context2.name}")

def main(Context, Relationship, df_context, df_relationship, reset_context=False):
    """
    Główna funkcja, która wykonuje całą operację od resetu bazy, przez zapis danych, po pobranie wyników.

    Args:
        Context (models.Model): Model Django dla tabeli 'Context'.
        Relationship (models.Model): Model Django dla tabeli 'Relationship'.
        df_context (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli 'Context'.
        df_relationship (pd.DataFrame): DataFrame zawierający dane do zapisania w tabeli 'Relationship'.
        reset_context (bool): Flaga określająca, czy resetować tabelę 'Context'.
    """
    # Zresetuj tabelę Relationship i opcjonalnie tabelę Context
    reset_relationship_table(Context, Relationship)
    reset_context_table(Context, reset_context)

    # Wprowadzenie nowych danych
    populate_context_table(Context, df_context)
    populate_relationship_table(Context, Relationship, df_relationship)

    # Pobranie i wyświetlenie danych z tabeli Relationship
    fetch_relationship_data(Relationship)

# Przykład użycia
if __name__ == "__main__":
    from optylogis.models import Context, Relationship

    # Przykładowe dane dla modelu Context z nowym polem 'description'
    data_context = {
        'name': ['Context A', 'Context B', 'Context C'],
        'description': ['Description for A', 'Description for B', 'Description for C']
    }

    # Tworzenie DataFrame dla Context
    df_context = pd.DataFrame(data_context)

    # Przykładowe dane dla modelu Relationship, gdzie odnosimy się do wartości 'name' w modelu Context
    data_relationship = {
        'context1_name': ['Context B', 'Context B', 'Context A'],
        'context2_name': ['Context A', 'Context A', 'Context C']
    }

    # Tworzenie DataFrame dla Relationship
    df_relationship = pd.DataFrame(data_relationship)

    # Uruchomienie głównej funkcji z opcjonalnym resetem bazy danych
    main(Context, Relationship, df_context, df_relationship, reset_context=False)
