import pandas as pd
from django.db import transaction
import os
import sys
from typing import Type
from django.db.models import Model

# Add project root directory to sys.path
sys.path.append('G:/PycharmProject/Timefold-training/optylogisdep')

# Set Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.settings')

# Import Django and setup Django environment
import django

django.setup()

# Import your Django model
from optylogis.models import Pers_gr


def df_to_django_model(df: pd.DataFrame, DjangoModel: Type[Model]) -> None:
    with transaction.atomic():
        for index, row in df.iterrows():
            obj, created = DjangoModel.objects.update_or_create(
                id=row.get('id'),
                defaults=row.to_dict()
            )
            if created:
                print(f"Created new record: {obj}")
            else:
                print(f"Updated existing record: {obj}")

    # Print all objects from DjangoModel after all the records have been updated/created
    for obj in DjangoModel.objects.all():
        print(obj)


# Example usage:
df = pd.DataFrame({
    'pers_st_id': [1, 2],
    'ium': ['001', '002'],
    'nr_sw': ['101', '102'],
    'data_nad': [pd.Timestamp('2020-11-02'), pd.Timestamp('2021-11-02')],
    'zaw': [True, True],
    'cof': [False, True],
    'ost_sp': [pd.Timestamp('2021-11-02'), pd.Timestamp('2022-11-02')],
})

df_to_django_model(df, Pers_gr)

print(Pers_gr.objects.all()[0].__dict__)
