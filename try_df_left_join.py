import pandas as pd
from tools.ODBCDataLoader import DataLoader
def main():
    dl = DataLoader(remove_csv_after_read=True)
    pers_gr = dl.pers_gr
    pers_st = dl.pers_st
    #print(pers_gr)
    #print(pers_st)

    #result = pd.merge(pers_gr, pers_st, how='left', on='l_pesel')
    result = pd.merge(pers_gr, pers_st, how='left', left_on='l_pesel', right_on='l_pesel')

    print(result.head())
    print(result.info())

if __name__ == '__main__':
    main()

