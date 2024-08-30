import os
import sys
from typing import Type, Dict, Tuple

import pandas as pd
from django.db import transaction, connection
from django.db.models import Model

from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django

django.setup()

from optylogis.models import Pers_st, Ksiazka_k


def reset_id_sequence(model_name: str):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{model_name}';")


def create_records_from_dataframe(df, model, foreign_keys_dict=None):
    model_fields = [field.name for field in model._meta.get_fields() if
                    not field.is_relation or field.many_to_one or field.one_to_one]

    df = df.fillna(value=pd.NA)  # pandas no longer has attribute 'np'
    for index, row in df.iterrows():
        data = row.to_dict()

        for key in data:
            if pd.isnull(data[key]):
                data[key] = None

        if foreign_keys_dict:
            foreign_keys = {key: data.pop(key) for key in foreign_keys_dict.keys() & data.keys()}
            keys = list(data.keys())
            data = {model._meta.get_field(field).name: data.pop(field) for field in keys if field in model_fields}

            add_row = True
            for foreign_key, (foreign_model, field) in foreign_keys_dict.items():
                if foreign_key in foreign_keys:
                    try:
                        foreign_obj = foreign_model.objects.get(**{field: foreign_keys[foreign_key]})
                        data[foreign_key] = foreign_obj
                    except foreign_model.DoesNotExist:
                        print(
                            f"No match for {field}: {foreign_keys[foreign_key]} in table {foreign_model._meta.db_table}, skipping row.")
                        add_row = False
                        break
            if add_row:
                model.objects.update_or_create(**data)  # change here
        else:
            print(f"Inserting data without foreign keys: {data}")
            model.objects.update_or_create(**data)  # change here


def print_all_records(model, verbose=False):
    for obj in model.objects.all():
        if verbose:
            print(obj.__dict__)


def df_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model],
                       foreign_keys_dict: Dict[str, Tuple[Type[Model], str]] = None,
                       verbose=False) -> None:
    with transaction.atomic():
        # DjangoModel.objects.all().delete()
        reset_id_sequence(DjangoModel._meta.db_table)
        create_records_from_dataframe(df, DjangoModel, foreign_keys_dict=foreign_keys_dict)

    if verbose:
        print(f"Wstawiono {DjangoModel.objects.all().count()} rekordów do {DjangoModel.__name__}")
    print_all_records(DjangoModel, verbose)


if __name__ == '__main__':
    dl = DataLoader()

    df_pers_st = dl.pers_st
    print("df_pers_st:", df_pers_st.head())
    df_to_django_model(df_pers_st, Pers_st, verbose=False)

    df_ksiazka_k = dl.ksiazka_k
    foreign_keys_pers_gr = {'k_do_pesel': (Pers_st, 'l_pesel'), 'k_bk_pesel': (Pers_st, 'l_pesel')}
    df_to_django_model(df_ksiazka_k, Ksiazka_k, foreign_keys_dict=foreign_keys_pers_gr, verbose=True)
