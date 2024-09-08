import os
import pandas as pd
from django.apps import apps
from optylogisdep.modules.timefold_optimizer.tools.settings import INDEX_PRACOWNI, EXCLUDED_WORDS_LIST

# Settings for pandas
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

# Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optylogisdep.optylogisdep.settings')

import django

django.setup()

# Fetching Django models
Indexy_4_updated = apps.get_model('optylogis', 'Indexy_4_updated')
Ksiazka_k = apps.get_model('optylogis', 'Ksiazka_k')

if __name__ == '__main__':
    # Get ksiazka_k_with_rbh: Data combined from Ksiazka_k with p_norma_k and p_norma_u columns from Indexy_4_updated
    ksiazka_k_updated = Ksiazka_k.get_ksiazka_k_with_rbh()

    # Convert QuerySet to DataFrame for ksiazka_k_with_rbh
    ksiazka_k_df = pd.DataFrame(list(ksiazka_k_updated.values()))

    # Display the first few rows and row count
    print(f"Ksiazka_k_with_rbh (Total rows: {len(ksiazka_k_df)}):")
    print(ksiazka_k_df.head())

    # Get uncalibrated devices in BOK: Devices assigned to a specific lab (INDEX_PRACOWNI) that have not been calibrated
    devices_uncalibrated_in_BOK = Ksiazka_k.get_uncalibrated_devices_in_BOK(pr_id=INDEX_PRACOWNI)

    # Convert QuerySet to DataFrame for uncalibrated devices
    devices_df = pd.DataFrame(list(devices_uncalibrated_in_BOK.values()))

    # Display the first few rows and row count
    print(f"Uncalibrated Devices in BOK (Total rows: {len(devices_df)}):")
    print(devices_df.head())

    # Get devices in BOK to assign: Devices filtered by exclusion criteria, ready to be assigned
    devices_in_BOK_to_assign = Ksiazka_k.devices_in_BOK_to_assign(pr_id=INDEX_PRACOWNI, excluded_words_list=EXCLUDED_WORDS_LIST)

    # Convert QuerySet to DataFrame for assignable devices
    devices_df_to_assign = pd.DataFrame(list(devices_in_BOK_to_assign.values()))

    # Display the first few rows and row count
    print(f"Devices in BOK to Assign (Total rows: {len(devices_df_to_assign)}):")
    print(devices_df_to_assign.head())
