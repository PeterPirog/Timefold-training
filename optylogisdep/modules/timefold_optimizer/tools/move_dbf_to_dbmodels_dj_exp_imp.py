import os
import pandas as pd
from django.apps import apps
from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader
from data_utils import create_resource_class, process_data, display_model_data_as_dataframe

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')
import django

django.setup()

if __name__ == "__main__":
    dl = DataLoader()
    verbose = False

    # Pobranie modeli Django
    Pers_st = apps.get_model('optylogis', 'Pers_st')
    Pers_gr = apps.get_model('optylogis', 'Pers_gr')
    Indexy_4 = apps.get_model('optylogis', 'Indexy_4')
    Osrodek_met = apps.get_model('optylogis', 'Osrodek_met')
    Ind4_om = apps.get_model('optylogis', 'Ind4_om')
    Uzytkownik = apps.get_model('optylogis', 'Uzytkownik')

    # Przykład z modelem Pers_st
    df_Pers_st = dl.pers_st
    if verbose: print(df_Pers_st)
    result_st = process_data(df_Pers_st, model=Pers_st)

    # Przykład z modelem Pers_gr
    df_Pers_gr = dl.pers_gr
    pers_gr_foreign_keys = {'l_pesel': (Pers_st, 'l_pesel')}
    df_ref_dict = {Pers_st: df_Pers_st}
    if verbose: print(df_Pers_gr.head())
    result_gr = process_data(df_Pers_gr, df_ref_dict=df_ref_dict, model=Pers_gr, foreign_keys=pers_gr_foreign_keys)

    # Przykład z modelem Indexy_4
    df_Indexy_4 = dl.indexy_4
    if verbose: print(df_Indexy_4)
    result_st = process_data(df_Indexy_4, model=Indexy_4)

    # Przykład z modelem Osrodek_met
    df_Osrodek_met = dl.osrodek_met
    if verbose: print(df_Osrodek_met)
    result_st = process_data(df_Osrodek_met, model=Osrodek_met)

    # Przykład z modelem Ind4_om
    df_Ind4_om = dl.ind4_om
    ind4_om_foreign_keys = {
        'indeks': (Indexy_4, 'indeks'),
        'om_id': (Osrodek_met, 'om_id')
    }
    df_ref_dict = {
        Indexy_4: df_Indexy_4,
        Osrodek_met: df_Osrodek_met
    }
    if verbose: print(df_Ind4_om)
    result_st = process_data(df_Ind4_om, df_ref_dict=df_ref_dict, model=Ind4_om, foreign_keys=ind4_om_foreign_keys)

    # Przykład z modelem Ind4_om
    df_Uzytkownik = dl.uzytkownik
    uzytkownik_foreign_keys = {
        'om_id': (Osrodek_met, 'om_id')
    }
    df_ref_dict = {
        Osrodek_met: df_Osrodek_met
    }
    if verbose: print(df_Uzytkownik)
    result_st = process_data(df_Uzytkownik, df_ref_dict=df_ref_dict, model=Uzytkownik,
                             foreign_keys=uzytkownik_foreign_keys)

    #########################

    # Wyświetlanie danych z modelu Pers_st jako DataFrame
    if verbose: display_model_data_as_dataframe(Pers_st)

    # Wyświetlanie danych z modelu Pers_gr jako DataFrame
    if verbose: display_model_data_as_dataframe(Pers_gr)

    # Wyświetlanie danych z modelu Indexy_4 jako DataFrame
    if verbose: display_model_data_as_dataframe(Indexy_4)

    # Wyświetlanie danych z modelu Osrodek_met jako DataFrame
    if verbose: display_model_data_as_dataframe(Osrodek_met)

    # Wyświetlanie danych z modelu Ind4_om jako DataFrame
    if verbose: display_model_data_as_dataframe(Ind4_om)

    # Wyświetlanie danych z modelu Ind4_om jako DataFrame
    display_model_data_as_dataframe(Uzytkownik)
