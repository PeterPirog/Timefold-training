import pandas as pd
import os
from collections import defaultdict
from django.apps import apps
from optylogisdep.modules.timefold_optimizer.tools.settings import INDEX_PRACOWNI

# Ustawienia wyświetlania dla pandas
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django
django.setup()

# Pobranie modeli Django
Pers_st = apps.get_model('optylogis', 'Pers_st')
Pers_gr = apps.get_model('optylogis', 'Pers_gr')
Ksiazka_k = apps.get_model('optylogis', 'Ksiazka_k')

if __name__ == '__main__':
    # Liczenie wszystkich rekordów w modelu Pers_gr
    print(f"Łączna liczba rekordów w modelu Pers_gr: {Pers_gr.objects.all().count()}")

    # Filtrowanie rekordów w modelu Pers_gr na podstawie warunków zaw=False, cof=False, oraz pr_id=INDEX_PRACOWNI
    filtered_pers_gr = Pers_gr.objects.filter(zaw=False, cof=False, l_pesel__pr_id__pr_id=INDEX_PRACOWNI)

    # Grupowanie wyników według osoby (używając pola l_nazw_im) i zbieranie listy IUM oraz l_pr_th i l_norma_p
    grouped_data = defaultdict(lambda: {'iums': [], 'l_pr_th': None, 'l_norma_p': None})
    for record in filtered_pers_gr:
        # Użycie kolumny l_nazw_im, która przechowuje pełne imię i nazwisko
        key = record.l_pesel.l_nazw_im
        grouped_data[key]['iums'].append(record.ium)
        # Dodanie l_pr_th tylko raz (jeśli nie jest jeszcze ustawione)
        if grouped_data[key]['l_pr_th'] is None:
            grouped_data[key]['l_pr_th'] = record.l_pesel.l_pr_th
        # Dodanie l_norma_p tylko raz (jeśli nie jest jeszcze ustawione)
        if grouped_data[key]['l_norma_p'] is None:
            grouped_data[key]['l_norma_p'] = record.l_pesel.l_norma_p

    # Wyświetlanie wyników w formacie: Imię Nazwisko, [lista IUM], l_pr_th, l_norma_p
    for person, data in grouped_data.items():
        pass
        #print(f"{person}, l_pr_th: {data['l_pr_th']}, l_norma_p: {data['l_norma_p']}, {data['iums']}")

    # Wyświetlanie wartości zmiennej INDEX_PRACOWNI
    print(f"INDEX_PRACOWNI: {INDEX_PRACOWNI}")


    print(f"Łączna liczba rekordów w modelu Ksiazka_k: {Ksiazka_k.objects.all().count()}")

    filtered_ksiazka_k=Ksiazka_k.objects.filter(pr_id__pr_id=INDEX_PRACOWNI)
    print(filtered_ksiazka_k.count())
    for record in filtered_ksiazka_k:
        print(record)