import os
import sys
import pandas as pd
from django.db import transaction, connection
from typing import Type, Dict
from django.db.models import Model
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader

# Ustawienie poprawnej ścieżki do katalogu projektu
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.append(project_root)

# Ustawienie zmiennej środowiskowej dla Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

# Importowanie Django i ustawienie środowiska Django
import django

django.setup()

# Importowanie modeli Django
from optylogis.models import Pers_st, Pers_gr, Indexy_4, Ind4_om, Osrodek_met, Ksiazka_k

from django.db import models

def reset_id_sequence(model_name: str):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{model_name}';")

def dataframe_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model], field_mapping: Dict[str, str] = None):
    try:
        # Usuń wszystkie istniejące dane z modelu
        DjangoModel.objects.all().delete()

        # Zresetuj sekwencję ID
        reset_id_sequence(DjangoModel._meta.db_table)

        # Pobierz wszystkie nazwy pól w modelu Django
        field_names = get_all_field_names(DjangoModel)

        for index, row in df.iterrows():
            # Utwórz słownik z kolumnami i wartościami odpowiadającymi polom modelu Django
            data = {}
            for field in field_names:
                # Mapuj kolumny DataFrame na pola modelu Django
                column_name = field_mapping.get(field, field) if field_mapping else field
                if column_name in df.columns:
                    data[field] = row[column_name]
                    print(f"Mapping column '{column_name}' to field '{field}'")
                else:
                    print(f"Column '{column_name}' not found in DataFrame")

            # Utwórz i zapisz nowy obiekt modelu Django
            obj = DjangoModel(**data)
            obj.save()

        print(f"Pomyślnie zapisano dane do modelu {DjangoModel.__name__}.")

    except Exception as e:
        print(f"Błąd podczas zapisywania danych do modelu {DjangoModel.__name__}: {e}")

def get_all_field_names(model: models.Model):
    return [field.name for field in model._meta.get_fields()]

if __name__ == '__main__':
    # Inicjalizacja obiektu DataLoader
    dl = DataLoader()

    # Załadowanie danych i zapisanie do odpowiednich modeli Django
    df_pers_st = dl.pers_st
    # df_pers_gr = dl.pers_gr
    # df_ksiazka_k = dl.ksiazka_k

    # Przykładowe mapowanie nazw pól modelu Django na nazwy kolumn w DataFrame
    field_mapping = {
        'l_nazwisko': 'l_nazwisko1', # 'field_name_in_django': 'column_name_in_dataframe'
        # Dodaj inne mapowania w razie potrzeby
    }

    keys = get_all_field_names(Pers_st)
    print(keys)

    # Zapisanie danych z DataFrame do modelu Django z uwzględnieniem mapowania pól
    dataframe_to_django_model(df_pers_st, Pers_st, field_mapping=field_mapping)
