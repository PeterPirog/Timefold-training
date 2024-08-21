import os
import sys
import pandas as pd
from django.db import transaction, connection
from typing import Type
from django.db.models import Model
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader

# Setting up the correct path to the project directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.append(project_root)

# Setting the environment variable for Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

# Importing Django and setting up Django environment
import django

django.setup()

# Importing Django models
from optylogis.models import Pers_st, Pers_gr


def reset_id_sequence(model_name: str):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{model_name}';")


def create_records_from_dataframe(df, model, foreign_key_field=None):
    for index, row in df.iterrows():
        data = row.to_dict()

        if foreign_key_field:
            # Attempt to find the Pers_st object based on l_pesel
            try:
                pers_st_obj = Pers_st.objects.get(l_pesel=data[foreign_key_field])
                data['pers_st'] = pers_st_obj  # Assigning the Pers_st object to the pers_st field
                del data[foreign_key_field]  # Remove the l_pesel field to prevent errors
            except Pers_st.DoesNotExist:
                print(f"No match for l_pesel: {data[foreign_key_field]} in table {model._meta.db_table}, skipping row.")
                continue  # Skip the current row
        model.objects.create(**data)


def print_all_records(model, verbose=False):
    for obj in model.objects.all():
        if verbose:
            print(obj.__dict__)


def df_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model], foreign_key_field: str = None,
                       verbose=False) -> None:
    with transaction.atomic():
        DjangoModel.objects.all().delete()
        reset_id_sequence(DjangoModel._meta.db_table)
        create_records_from_dataframe(df, DjangoModel, foreign_key_field=foreign_key_field)

    print_all_records(DjangoModel, verbose)


if __name__ == '__main__':
    dl = DataLoader()

    df_pers_st = dl.pers_st
    df_to_django_model(df_pers_st, Pers_st, verbose=False)

    df_pers_gr = dl.pers_gr
    df_to_django_model(df_pers_gr, Pers_gr, foreign_key_field='l_pesel', verbose=True)
