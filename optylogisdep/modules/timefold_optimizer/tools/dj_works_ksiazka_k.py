import pandas as pd
import os
from django.apps import apps

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

if __name__ == '__main__':

    # Użycie metody get_uncalibrated_devices_in_BOK z modelu Ksiazka_k
    devices_uncalibrated_in_BOK = Ksiazka_k.get_uncalibrated_devices_in_BOK(pr_id=INDEX_PRACOWNI)
    print(devices_uncalibrated_in_BOK)

    # Użycie metody devices_in_BOK_to_assign z modelu Ksiazka_k, aby przefiltrować urządzenia do przypisania
    devices_in_BOK_to_assign = Ksiazka_k.devices_in_BOK_to_assign(pr_id=INDEX_PRACOWNI, excluded_words_list=EXCLUDED_WORDS_LIST)
    print(devices_in_BOK_to_assign)

    # Konwersja QuerySet na DataFrame przy pomocy funkcji queryset_to_dataframe
    df = queryset_to_dataframe(devices_in_BOK_to_assign)

    # Wyświetlenie wyników w formacie DataFrame
    print(df.head())
    print(df.info())
