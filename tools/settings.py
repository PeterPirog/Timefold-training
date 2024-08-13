import os

LOGIS_DIRECTORY = r"D:\PycharmProjects\django-odbc\Logis"
DATE_COLUM_LIST=['DATA_NAD','OST_SP']


# DBF files paths
dbf_paths={}
dbf_paths['bok']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'bok.DBF')
dbf_paths['bok_arch']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'bok_arch.DBF')
dbf_paths['index_4']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'indexy_4.DBF')
dbf_paths['pers_gr']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'pers_gr.DBF')
dbf_paths['pers_st']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'pers_st.DBF')
dbf_paths['ksiazka_k']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'ksiazka_k.DBF')
dbf_paths['ksiazka_k_arch']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'ksiazka_k_arch.DBF')
dbf_paths['om_zu']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'om_zu.DBF')
dbf_paths['pdf_protspr']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'pdf_protspr.DBF')
dbf_paths['przyrzad_zmcbd']=os.path.join(LOGIS_DIRECTORY, 'DANE', 'przyrzad_zmcbd.DBF')


dbf_paths['uzytkownik']=os.path.join(LOGIS_DIRECTORY, 'DANE_SIM', 'uzytkownik.DBF')
dbf_paths['osrodek_met']=os.path.join(LOGIS_DIRECTORY, 'DANE_SIM', 'osrodek_met.DBF')
dbf_paths['osrodek_pr']=os.path.join(LOGIS_DIRECTORY, 'DANE_SIM', 'osrodek_pr.DBF')
dbf_paths['pyt_podstawa']=os.path.join(LOGIS_DIRECTORY, 'DANE_SIM', 'pyt_podstawa.DBF')


