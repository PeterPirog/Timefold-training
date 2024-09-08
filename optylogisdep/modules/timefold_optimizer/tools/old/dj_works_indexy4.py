import pandas as pd
import os
from django.apps import apps
from data_utils import queryset_to_dataframe, update_indexy_4_updated

# Ustawienia wyświetlania dla pandas
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django
django.setup()

# Pobranie modeli Django
Ind4_om = apps.get_model('optylogis', 'Ind4_om')
Indexy_4 = apps.get_model('optylogis', 'Indexy_4')
Indexy_4_updated = apps.get_model('optylogis', 'Indexy_4_updated')

def save_to_excel(df, filename):
    """
    Funkcja zapisująca DataFrame do pliku Excel.

    Args:
        df (pd.DataFrame): DataFrame do zapisania
        filename (str): Nazwa pliku, do którego ma być zapisany DataFrame
    """
    df.to_excel(filename, index=False)
    print(f"Dane zostały zapisane do pliku {filename}")

def compare_records(updated_records_db, updated_records_mem):
    """
    Funkcja porównująca rekordy z tabeli Indexy_4_updated i wyników z pamięci (get_updated_queryset).

    Args:
        updated_records_db (QuerySet): Zaktualizowane rekordy z bazy danych (Indexy_4_updated)
        updated_records_mem (QuerySet): Zaktualizowane rekordy w pamięci (wynik get_updated_queryset)

    Returns:
        None: Wyświetla różnice w konsoli
    """
    # Sprawdź, czy liczba rekordów jest taka sama
    if updated_records_db.count() != updated_records_mem.count():
        print(f"Liczba rekordów jest różna: {updated_records_db.count()} w bazie vs {updated_records_mem.count()} w pamięci")
        return

    # Iteracja po rekordach z bazy danych i z pamięci
    for db_record, mem_record in zip(updated_records_db, updated_records_mem):
        differences = []

        # Porównanie poszczególnych pól
        if db_record.indeks != mem_record.indeks:
            differences.append(f"indeks: {db_record.indeks} != {mem_record.indeks}")
        if db_record.nazwa != mem_record.nazwa:
            differences.append(f"nazwa: {db_record.nazwa} != {mem_record.nazwa}")
        if db_record.p_pwaz_k != mem_record.updated_p_pwaz_k:
            differences.append(f"p_pwaz_k: {db_record.p_pwaz_k} != {mem_record.updated_p_pwaz_k}")
        if db_record.p_pwaz_u != mem_record.updated_p_pwaz_u:
            differences.append(f"p_pwaz_u: {db_record.p_pwaz_u} != {mem_record.updated_p_pwaz_u}")
        if db_record.p_norma_k != mem_record.updated_p_norma_k:
            differences.append(f"p_norma_k: {db_record.p_norma_k} != {mem_record.updated_p_norma_k}")
        if db_record.p_norma_u != mem_record.updated_p_norma_u:
            differences.append(f"p_norma_u: {db_record.p_norma_u} != {mem_record.updated_p_norma_u}")

        # Wyświetlenie różnic
        if differences:
            print(f"Różnice dla indeksu {db_record.indeks}:")
            for diff in differences:
                print(f"  - {diff}")

    print("Porównanie zakończone.")


if __name__ == '__main__':
    # Wywołanie funkcji aktualizującej tabelę Indexy_4_updated
    updated_records_db = update_indexy_4_updated(Indexy_4, Indexy_4_updated, Ind4_om)

    # Wywołanie metody get_updated_queryset z modelu Indexy_4
    updated_queryset_mem = Indexy_4.get_updated_queryset(Ind4_om)

    # Konwersja danych do DataFrame'ów
    df_updated_db = queryset_to_dataframe(updated_records_db)
    df_updated_mem = queryset_to_dataframe(updated_queryset_mem)

    # Wyświetlenie danych z bazy (Indexy_4_updated)
    print("Dane z bazy (Indexy_4_updated):")
    print(df_updated_db.tail())
    print(df_updated_db.info())

    # Wyświetlenie zaktualizowanych danych w pamięci (get_updated_queryset)
    print("Dane w pamięci (get_updated_queryset):")
    print(df_updated_mem.tail())
    print(df_updated_mem.info())

    # Zapisanie danych do plików Excel
    save_to_excel(df_updated_db, 'indexy_4_updated_db.xlsx')
    save_to_excel(df_updated_mem, 'indexy_4_updated_mem.xlsx')

    # Porównanie rekordów z bazy danych i z pamięci
    compare_records(updated_records_db, updated_queryset_mem)
