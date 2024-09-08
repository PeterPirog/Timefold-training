import pandas as pd
import os
from django.apps import apps
from data_utils import compare_and_remove_missing

# Ustawienia wyświetlania dla pandas
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django
django.setup()


if __name__ == '__main__':
    # Pobranie modeli Django
    Ind4_om = apps.get_model('optylogis', 'Ind4_om')
    Indexy_4 = apps.get_model('optylogis', 'Indexy_4')

    # Wywołanie funkcji porównującej i usuwającej brakujące rekordy
    compare_and_remove_missing(Ind4_om, Indexy_4, 'indeks', 'indeks')
