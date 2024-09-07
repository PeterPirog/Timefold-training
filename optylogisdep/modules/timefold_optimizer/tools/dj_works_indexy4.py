import pandas as pd
import os
from django.apps import apps
from django.db.models.functions import Length
from django.db import transaction

from optylogisdep.modules.timefold_optimizer.tools.settings import INDEX_PRACOWNI, EXCLUDED_WORDS_LIST
from data_utils import queryset_to_dataframe

# Ustawienia wyświetlania dla pandas
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django
django.setup()

# Pobranie modeli Django
Ksiazka_k = apps.get_model('optylogis', 'Ksiazka_k')
Ind4_om = apps.get_model('optylogis', 'Ind4_om')
Indexy_4 = apps.get_model('optylogis', 'Indexy_4')
Indexy_4_updated = apps.get_model('optylogis', 'Indexy_4_updated')

if __name__ == '__main__':
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

    # Filtrujemy rekordy w Indexy_4_updated, gdzie długość pola 'indeks' wynosi 11
    indexy_4_updated_records = Indexy_4_updated.objects.annotate(indeks_length=Length('indeks')).filter(indeks_length=11)

    # Licznik zaktualizowanych rekordów
    updated_count = 0

    # Iteracja przez wybrane rekordy
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

            print(f"Zaktualizowano rekord o indeksie: {record.indeks}")

        except Ind4_om.DoesNotExist:
            pass


    print(f"Aktualizacja zakończona. Zaktualizowano {updated_count} rekordów.")

    # Wyświetl dane w formacie pandas dataframe
    df = queryset_to_dataframe(indexy_4_updated_records)
    print(df.tail())
    print(df.info())
