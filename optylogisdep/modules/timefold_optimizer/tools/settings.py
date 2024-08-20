import os

# Instead of using relative paths, use absolute paths to the directories
PROJECT_ROOT =os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..','..')


#sys.path.append(os.path.join(BASE_DIR, '../../modules'))


print(PROJECT_ROOT)
LOGIS_DIRECTORY = os.path.join(PROJECT_ROOT, 'Logis')  # place for define the Logis directory with data

PYTHON_32BIT_INTERPRETER = os.path.join(PROJECT_ROOT, 'venv32/Scripts/python')
ODBC_READ_SCRIPT_PATH = os.path.join(PROJECT_ROOT, 'optylogisdep/modules/timefold_optimizer/tools//dbf_to_csv_transformation_32bit.py')
CSV_FILES_PATH = os.path.join(PROJECT_ROOT, 'optylogisdep/modules/timefold_optimizer/tools/CSV_files')

# Base directory for DBF files, make sure the path is valid and accessible
CONNECTION_STRING = 'DSN=VisualFoxProDSN;SourceDB={directory};Exclusive=No;BackgroundFetch=Yes;Collate=Machine;Null=Yes;Deleted=No;'

# Tables in the DANE and DANE_SIM directories
DBF_TABLES_PATH_DANE = [
    'bok', 'bok_arch', 'indexy_4','ind4_om', 'pers_gr', 'pers_st',
    'ksiazka_k', 'om_zu', 'pdf_protspr', 'przyrzad_zmcbd','ind4_om','terminy','pers_nob'
]
# 'ksiazka_k_arch' is ignored becasue is too big for 32-bit ODBC read without chunks
DBF_TABLES_PATH_DANE_SIM = [
    'uzytkownik', 'osrodek_met', 'osrodek_pr', 'pyt_podstawa','pers_ob'
]

DATE_COLUMN_LIST = ['DATA_NAD', 'OST_SP', 'data_nad', 'ost_sp', 'k_do_data', 'k_do_datap', 'k_do_ddata', 'k_bk_data',
                    'k_bk_dec', 'k_bk_ddata',
                    'k_data_sp', 'k_data_wa', 'k_data_kp', 'ostatni', 'k_data_kj', 'k_data_kz', 'k_data_spp',
                    'k_data_spk', 'l_kl3', 'l_kl2', 'l_kl1', 'l_klm', 'l_ur','u_data_p','u_data_w']

# Some columns with number which should be treated as a string not a number
STRING_COLUMN_LIST = ['indeks', 'ium', 'pr_id', 'st_id','k_do_pesel', 'k_do_pin', 'k_pr_sp','p_nr_fab','u_id']
NUMERIC_COLUMN_LIST = ['l_norma_p']

def generate_dbf_paths(tables, directory):
    """Generate paths for DBF files."""
    return {table: os.path.join(directory, f"{table}.DBF") for table in tables}


# Generate paths using actual, existing and accessible directories
dbf_paths_dane = generate_dbf_paths(DBF_TABLES_PATH_DANE, os.path.join(LOGIS_DIRECTORY, 'DANE'))
dbf_paths_dane_sim = generate_dbf_paths(DBF_TABLES_PATH_DANE_SIM, os.path.join(LOGIS_DIRECTORY, 'DANE_SIM'))

DBF_PATHS = {**dbf_paths_dane, **dbf_paths_dane_sim}

###  CONSTANTS FOR TIMEFOLD
INDEX_PRACOWNI = '9111497111'  #index to select technician and devices from the same unit of organization

# Example usage:
if __name__ == "__main__":
    for key, value in DBF_PATHS.items():
        print(f"Table: {key}, Path: {value}")
