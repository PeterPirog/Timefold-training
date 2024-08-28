from optylogisdep.modules.timefold_optimizer.tools.ODBCDataLoader import DataLoader
from optylogisdep.modules.timefold_optimizer.tools.df_merges import uncalibrated_devices_in_bok
import pandas as pd
pd.set_option("display.max_columns", None)


def main():
    dl = DataLoader(remove_csv_after_read=True)
    ksiazka_k = dl.ksiazka_k
    not_nan_ksiazka_k = ksiazka_k[ksiazka_k['k_uwagi'].notna()]
    print(not_nan_ksiazka_k)


if __name__ == '__main__':
    main()
    #print(uncalibrated_devices_in_bok)

