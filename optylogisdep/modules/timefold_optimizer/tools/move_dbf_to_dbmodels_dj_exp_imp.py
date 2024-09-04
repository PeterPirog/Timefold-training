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
    Osrodek_pr = apps.get_model('optylogis', 'Osrodek_pr')
    Ksiazka_k = apps.get_model('optylogis', 'Ksiazka_k')
    Przyrzad_zmcbd = apps.get_model('optylogis', 'Przyrzad_zmcbd')
    Bok = apps.get_model('optylogis', 'Bok')

    # 1. Osrodek_pr
    df_Osrodek_pr = dl.osrodek_pr
    result_osrodek_pr = process_data(df_Osrodek_pr, model=Osrodek_pr)

    # 2. Osrodek_met
    df_Osrodek_met = dl.osrodek_met
    result_osrodek_met = process_data(df_Osrodek_met, model=Osrodek_met)

    # 3. Indexy_4
    df_Indexy_4 = dl.indexy_4
    result_indexy_4 = process_data(df_Indexy_4, model=Indexy_4)

    # 4. Pers_st
    df_Pers_st = dl.pers_st
    pers_st_foreign_keys = {'pr_id': (Osrodek_pr, 'pr_id')}
    df_ref_dict = {Osrodek_pr: df_Osrodek_pr}
    result_pers_st = process_data(df_Pers_st, df_ref_dict=df_ref_dict, model=Pers_st, foreign_keys=pers_st_foreign_keys)

    # 5. Uzytkownik
    df_Uzytkownik = dl.uzytkownik
    uzytkownik_foreign_keys = {'om_id': (Osrodek_met, 'om_id')}
    df_ref_dict = {Osrodek_met: df_Osrodek_met}
    result_uzytkownik = process_data(df_Uzytkownik, df_ref_dict=df_ref_dict, model=Uzytkownik, foreign_keys=uzytkownik_foreign_keys)

    # 6. Ind4_om
    df_Ind4_om = dl.ind4_om
    ind4_om_foreign_keys = {
        'indeks': (Indexy_4, 'indeks'),
        'om_id': (Osrodek_met, 'om_id')
    }
    df_ref_dict = {
        Indexy_4: df_Indexy_4,
        Osrodek_met: df_Osrodek_met
    }
    result_ind4_om = process_data(df_Ind4_om, df_ref_dict=df_ref_dict, model=Ind4_om, foreign_keys=ind4_om_foreign_keys)

    # 7. Przyrzad_zmcbd
    df_Przyrzad_zmcbd = dl.przyrzad_zmcbd
    przyrzad_zmcbd_foreign_keys = {
        'indeks': (Indexy_4, 'indeks'),
        'u_id': (Uzytkownik, 'u_id'),
        'om_id': (Osrodek_met, 'om_id'),
        'pr_id': (Osrodek_pr, 'pr_id'),
        'p_zm_id': (Uzytkownik, 'u_id')
    }
    df_ref_dict = {
        Indexy_4: df_Indexy_4,
        Uzytkownik: df_Uzytkownik,
        Osrodek_met: df_Osrodek_met,
        Osrodek_pr: df_Osrodek_pr
    }
    result_przyrzad_zmcbd = process_data(df_Przyrzad_zmcbd, df_ref_dict=df_ref_dict, model=Przyrzad_zmcbd, foreign_keys=przyrzad_zmcbd_foreign_keys)

    # 8. Bok
    df_Bok = dl.bok
    bok_foreign_keys = {
        'pr_id': (Osrodek_pr, 'pr_id'),
        'u_id': (Uzytkownik, 'u_id'),
        'k_do_pesel': (Pers_st, 'l_pesel'),
        'k_bk_pesel': (Pers_st, 'l_pesel'),
        'p_ind_rek': (Przyrzad_zmcbd, 'ind_rek'),
        'om_pracow': (Osrodek_met, 'om_id'),
        'indeks': (Indexy_4, 'indeks')
    }
    df_ref_dict = {
        Osrodek_pr: df_Osrodek_pr,
        Uzytkownik: df_Uzytkownik,
        Pers_st: df_Pers_st,
        Przyrzad_zmcbd: df_Przyrzad_zmcbd,
        Osrodek_met: df_Osrodek_met,
        Indexy_4: df_Indexy_4
    }
    result_bok = process_data(df_Bok, df_ref_dict=df_ref_dict, model=Bok, foreign_keys=bok_foreign_keys)

    # 9. Ksiazka_k
    df_Ksiazka_k = dl.ksiazka_k

    # Definiowanie kluczy obcych dla modelu Ksiazka_k
    ksiazka_k_foreign_keys = {
        'pr_id': (Osrodek_pr, 'pr_id'),           # Klucz obcy do modelu Osrodek_pr
        'k_do_pesel': (Pers_st, 'l_pesel'),       # Klucz obcy do modelu Pers_st
        'k_bk_pesel': (Pers_st, 'l_pesel'),       # Klucz obcy do modelu Pers_st
        'indeks': (Indexy_4, 'indeks'),           # Klucz obcy do modelu Indexy_4
        'p_ind_rek': (Przyrzad_zmcbd, 'ind_rek'), # Klucz obcy do modelu Przyrzad_zmcbd
        'bk_id': (Bok, 'bk_id')                   # Klucz obcy do modelu Bok
    }

    # Tworzenie słownika referencyjnego zawierającego odpowiednie DataFrame'y
    df_ref_dict = {
        Osrodek_pr: df_Osrodek_pr,
        Pers_st: df_Pers_st,
        Indexy_4: df_Indexy_4,
        Przyrzad_zmcbd: df_Przyrzad_zmcbd,
        Bok: df_Bok  # Dodanie referencji do modelu Bok
    }

    # Przetwarzanie danych dla modelu Ksiazka_k
    result_ksiazka_k = process_data(
        df_Ksiazka_k,
        df_ref_dict=df_ref_dict,
        model=Ksiazka_k,
        foreign_keys=ksiazka_k_foreign_keys
    )

    # 10. Pers_gr (on the assumption that Pers_gr depends on Pers_st)
    df_Pers_gr = dl.pers_gr
    pers_gr_foreign_keys = {'l_pesel': (Pers_st, 'l_pesel')}
    df_ref_dict = {Pers_st: df_Pers_st}
    result_pers_gr = process_data(df_Pers_gr, df_ref_dict=df_ref_dict, model=Pers_gr, foreign_keys=pers_gr_foreign_keys)
    #########################

    # Wyświetlanie danych z modelu Pers_st jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Pers_st)

    # Wyświetlanie danych z modelu Pers_gr jako DataFrames
    if verbose:
        display_model_data_as_dataframe(Pers_gr)

    # Wyświetlanie danych z modelu Indexy_4 jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Indexy_4)

    # Wyświetlanie danych z modelu Osrodek_met jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Osrodek_met)

    # Wyświetlanie danych z modelu Ind4_om jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Ind4_om)

    # Wyświetlanie danych z modelu Uzytkownik jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Uzytkownik)

    # Wyświetlanie danych z modelu Osrodek_pr jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Osrodek_pr)

    # Wyświetlanie danych z modelu Przyrzad_zmcbd jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Przyrzad_zmcbd)

    # Wyświetlanie danych z modelu Bok jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Bok)

    # Wyświetlanie danych z modelu Ksiazka_k jako DataFrame
    if verbose:
        display_model_data_as_dataframe(Ksiazka_k)
