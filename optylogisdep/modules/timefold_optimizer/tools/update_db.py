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
from optylogis.models import Pers_st, Pers_gr, Indexy_4, Ind4_om, Osrodek_met


def reset_id_sequence(model_name: str):
    with connection.cursor() as cursor:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{model_name}';")


def create_records_from_dataframe(df, model, foreign_key_field=None, foreign_model=None, foreign_key_lookup=None):
    for index, row in df.iterrows():
        data = row.to_dict()

        if foreign_key_field and foreign_model and foreign_key_lookup:
            # Attempt to find the foreign key object based on the column in DataFrame
            try:
                foreign_obj = foreign_model.objects.get(**{foreign_key_lookup: data[foreign_key_field]})
                data[
                    foreign_model.__name__.lower()] = foreign_obj  # Assigning the foreign key object to the appropriate field
                del data[foreign_key_field]  # Remove the foreign key field to prevent errors
            except foreign_model.DoesNotExist:
                print(
                    f"No match for {foreign_key_lookup}: {data[foreign_key_field]} in table {model._meta.db_table}, skipping row.")
                continue  # Skip the current row if the foreign key does not exist

        model.objects.create(**data)


def print_all_records(model, verbose=False):
    for obj in model.objects.all():
        if verbose:
            print(obj.__dict__)


def df_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model], foreign_key_field: str = None,
                       foreign_model: Type[Model] = None, foreign_key_lookup: str = None, verbose=False) -> None:
    with transaction.atomic():
        DjangoModel.objects.all().delete()
        reset_id_sequence(DjangoModel._meta.db_table)
        create_records_from_dataframe(df, DjangoModel, foreign_key_field=foreign_key_field,
                                      foreign_model=foreign_model, foreign_key_lookup=foreign_key_lookup)
    print_all_records(DjangoModel, verbose)


if __name__ == '__main__':
    dl = DataLoader()

    df_pers_st = dl.pers_st
    df_to_django_model(df_pers_st, Pers_st, verbose=False)

    df_pers_gr = dl.pers_gr
    df_to_django_model(df_pers_gr, Pers_gr, foreign_key_field='l_pesel', foreign_model=Pers_st,
                       foreign_key_lookup='l_pesel', verbose=False)

    df_indexy_4 = dl.indexy_4
    df_to_django_model(df_indexy_4, Indexy_4, verbose=False)

    df_osrodek_met = dl.osrodek_met
    df_to_django_model(df_osrodek_met, Osrodek_met, verbose=False)

    df_ind4_om = dl.ind4_om
    df_to_django_model(df_ind4_om, Ind4_om, foreign_key_field='om_id', foreign_model=Osrodek_met,
                       foreign_key_lookup='om_id', verbose=True)
