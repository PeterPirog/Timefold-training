import pandas as pd

pd.set_option("display.max_columns", None)
import os
from django.apps import apps
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader
from tablib import Dataset

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django

django.setup()

# Definicje modeli
Pers_st = apps.get_model('optylogis', 'Pers_st')
Pers_gr = apps.get_model('optylogis', 'Pers_gr')


def get_model_fields(model):
    return [field.name for field in model._meta.fields]


class BaseResource(resources.ModelResource):
    @classmethod
    def get_fields(cls, model):
        return get_model_fields(model)


class PersStResource(BaseResource):
    class Meta:
        model = Pers_st
        fields = BaseResource.get_fields(model)
        import_id_fields = ('l_pesel',)


class PersGrResource(BaseResource):
    l_pesel = fields.Field(
        column_name='l_pesel',
        attribute='l_pesel',
        widget=ForeignKeyWidget(Pers_st, 'l_pesel')
    )

    class Meta:
        model = Pers_gr
        fields = BaseResource.get_fields(model)
        import_id_fields = ('l_pesel', 'ium')


def verify_and_remove_missing_pesel(df_gr, df_st, key):
    missing_pesel = df_gr[~df_gr[key].isin(df_st[key])]
    if not missing_pesel.empty:
        print(f"Brakujące rekordy {key} w źródłowym dataframe:")
        print(missing_pesel)
        df_gr = df_gr[df_gr[key].isin(df_st[key])]
    return df_gr


def load_data(resource_class, df):
    resource = resource_class()
    dataset = Dataset().load(df.to_csv(index=False), format='csv')
    result = resource.import_data(dataset, raise_errors=True, dry_run=False)
    return result


def process_data(df, df_ref, resource_class, key):
    df = verify_and_remove_missing_pesel(df, df_ref, key)
    result = load_data(resource_class, df)
    return result


if __name__ == "__main__":
    dl = DataLoader()

    df_Pers_st = dl.pers_st
    print(df_Pers_st)
    result_st = load_data(PersStResource, df_Pers_st)

    df_Pers_gr = dl.pers_gr
    print(df_Pers_gr.head())
    print(df_Pers_gr.columns)

    result_gr = process_data(df_Pers_gr, df_Pers_st, PersGrResource, 'l_pesel')
