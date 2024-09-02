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

# Paths to DBF tables within the 'DANE' directory
DBF_TABLES_PATH_DANE = [
    'bok',               # Main BOK table
    'bok_arch',          # Archived BOK data
    'indexy_4',          # Indexes table
    'ind4_om',           # OM indexes table
    'pers_gr',           # Group personnel data
    'pers_st',           # Station personnel data
    'ksiazka_k',         # Book of calibration logs
    'om_zu',             # OM operations table
    'pdf_protspr',       # PDF protocols for sample protection
    'przyrzad_zmcbd',    # Devices and equipment data
    'ind4_om',           # OM indexes table (duplicate, might need to check if intentional)
    'terminy',           # Deadlines table
    'pers_nob'           # Non-operational personnel data
]

# Paths to DBF tables within the 'DANE_SIM' directory
DBF_TABLES_PATH_DANE_SIM = [
    'uzytkownik',        # Users data
    'osrodek_met',       # Metrological centers
    'osrodek_pr',        # PR centers
    'pyt_podstawa',      # Base questions or criteria
    'pers_ob'            # Operational personnel data
]

# List of columns containing only dates (without time)
DATE_DAY_COLUMN_LIST = [
    'l_ur',          # Data urodzenia (Date of birth)
    'k_data_sp',     # Data sprawdzenia przyrządu (Date of instrument inspection)
    'k_data_wa',     # Termin ważności przyrządu po kalibracji (Validity date after calibration)
    'k_data_kp',     # Data podpisania protokołu sprawdzenia przez kierownika pracowni (Date of signing the inspection protocol by the workshop manager)
    'k_data_kj',     # Data podpisania protokołu stanu technicznego przez spec. ds. jakości (Date of signing the technical condition protocol by the quality specialist)
    'k_data_kz',     # Data podpisania protokołu stanu technicznego przez kierownika zakładu (Date of signing the technical condition protocol by the plant manager)
    'u_data_p',      # Data przyjęcia do depozytu (Date of acceptance into the deposit)
    'u_data_w',      # Data wydania z depozytu (Date of release from the deposit)
    'k_do_data'      # Data skierowania przyrządu przez BOK do kalibracji (Date the instrument was sent by BOK for calibration)
]

# List of columns containing dates with times
DATE_HOUR_COLUMN_LIST = [
    'k_do_datap',    # Data pobrania przyrządu z BOK przez wykonawcę prac (Date and time of instrument retrieval from BOK by the worker)
    'k_do_ddata',    # Data zlecenia prac przez kierownika pracowni (Date and time the work was commissioned by the workshop manager)
    'k_bk_ddata',    # Data wydania zlecenia przez kierownika pracowni o przekazaniu przyrządu do BOK po pracach (Date and time of issuing the order by the workshop manager to transfer the instrument to BOK after the work)
    'k_bk_data'      # Data przyjęcia przyrządu do BOK po wykonaniu prac (Date and time of acceptance of the instrument to BOK after the work)
]

# Columns to be treated as strings instead of numbers
STRING_COLUMN_LIST = [
    'indeks',        # Index identifier
    'ium',           # IUM identifier
    'pr_id',         # PR identifier
    'st_id',         # Station identifier
    'k_do_pesel',    # PESEL number for calibration personnel
    'k_do_pin',      # PIN for calibration personnel
    'k_pr_sp',       # Calibration process number
    'p_nr_fab',      # Device serial number
    'u_id',          # User ID
    'om_id'          # OM identifier
]

# Columns to be treated as numeric values
NUMERIC_COLUMN_LIST = [
    'l_norma_p'      # Personnel norm value
]

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
