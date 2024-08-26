import os
import sys
import pandas as pd
from django.db import connection
from typing import Type, Dict
from django.db.models import Model
from django.db import models
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

def reset_id_sequence(model_name: str):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{model_name}';")


def dataframe_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model], field_mapping: Dict[str, str] = None):
    df.columns = df.columns.str.strip()

    try:
        DjangoModel.objects.all().delete()
        reset_id_sequence(DjangoModel._meta.db_table)
        model_fields = set([field.name for field in DjangoModel._meta.get_fields()])

        for index, row in df.iterrows():
            data = {}
            for column in df.columns:
                field_name = field_mapping.get(column, column) if field_mapping else column
                if field_name in model_fields:
                    field = DjangoModel._meta.get_field(field_name)
                    if field.is_relation and field.many_to_one:
                        related_model = field.related_model
                        related_obj = related_model.objects.filter(l_pesel=row[column]).first()
                        if related_obj is None:
                            raise ValueError(
                                f"Related item with key '{row[column]}' in the model '{related_model.__name__}' does not exist.")
                        data[field_name] = related_obj
                    else:
                        data[field_name] = row[column]
                else:
                    raise ValueError(
                        f"Kolumna '{column}' nie może być dopasowana do żadnego pola w modelu '{DjangoModel.__name__}'.")

            obj = DjangoModel(**data)
            obj.save()

        print(f"Pomyślnie zapisano dane do modelu {DjangoModel.__name__}.")

    except ValueError as ve:
        print(f"Błąd: {ve}")
    except Exception as e:
        print(f"Błąd podczas zapisywania danych do modelu {DjangoModel.__name__}: {e}")

def get_all_field_names(model: models.Model):
    return [field.name for field in model._meta.get_fields()]

if __name__ == '__main__':
    dl = DataLoader()

    df_pers_st = dl.pers_st
    dataframe_to_django_model(df_pers_st, Pers_st, field_mapping=None)

    df_pers_gr = dl.pers_gr
    print("DataFrame columns:", df_pers_gr.columns.tolist())
    field_mapping_pers_gr = {
        'l_pesel': 'pers_st'
    }
    dataframe_to_django_model(df_pers_gr, Pers_gr, field_mapping=field_mapping_pers_gr)

    df_indexy_4 = dl.indexy_4
    dataframe_to_django_model(df_indexy_4, Indexy_4, field_mapping=None)

    df_osrodek_met = dl.osrodek_met
    dataframe_to_django_model(df_osrodek_met, Osrodek_met, field_mapping=None)

    df_ind4_om = dl.ind4_om
    print("DataFrame columns:", df_ind4_om.columns.tolist())
   # field_mapping_ind4_om = {
    #    'om_id': 'osrodek_met'
    #}
    #dataframe_to_django_model(df_ind4_om, Ind4_om, field_mapping=field_mapping_ind4_om)
    dataframe_to_django_model(df_ind4_om, Ind4_om, field_mapping=None)

