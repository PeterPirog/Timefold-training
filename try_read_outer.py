from tools.ODBCDataLoader import DataLoader
def main():
    dl = DataLoader(remove_csv_after_read=True)
    pers_gr = dl.pers_gr
    print(pers_gr)


if __name__ == '__main__':
    main()

