from tools.ODBCDataLoader import DataLoader

def main():
    dl = DataLoader()
    ksiazka_k = dl.ksiazka_k
    print(ksiazka_k.head())


if __name__ == '__main__':
    main()
