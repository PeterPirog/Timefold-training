import pandas as pd
from tools.ODBCDataLoader import DataLoader

# Załaduj dane
ksiazka_k = DataLoader().ksiazka_k
indexy_4 = DataLoader().indexy_4

###### DO POPRAWY ###################### Wyniki liczbowe są błene, zła filtracja



# Przygotuj indeksy do łączenia
indexy_4['indeks'] = indexy_4['indeks'].str[:11]

# Połącz dane na podstawie pierwszych 11 znaków z kolumny 'indeks'
merged_df = ksiazka_k.merge(indexy_4, how='left', left_on=ksiazka_k['indeks'].str[:11], right_on='indeks')

# Konwersja kolumny k_do_datap do formatu daty
merged_df['k_do_datap'] = pd.to_datetime(merged_df['k_do_datap'])

# Warunki logiczne
merged_df['count_condition'] = (merged_df['k_do_datap'] > '2000-01-01').astype(int)
merged_df['p_norma_condition'] = merged_df['count_condition'] * merged_df['p_norma_k']

# Grupowanie i agregowanie wyników
result = merged_df[merged_df['k_bk_data'].isnull() & merged_df['k_do_nazw'].str.strip() != ''].groupby('k_do_nazw').agg(
    Przydzielono=pd.NamedAgg(column='k_do_nazw', aggfunc='count'),
    Pobrano=pd.NamedAgg(column='count_condition', aggfunc='sum'),
    Przydzielono_rbh=pd.NamedAgg(column='p_norma_k', aggfunc='sum'),
    Pobrano_rbh=pd.NamedAgg(column='p_norma_condition', aggfunc='sum'),
)

# Obliczanie Rbh czekające na pobranie
result['Rbh_czekajace_na_pobranie'] = result['Przydzielono_rbh'] - result['Pobrano_rbh']

# Sortowanie wyników według 'Rbh czekajace na pobranie'
result = result.sort_values(by='Rbh_czekajace_na_pobranie', ascending=True)

# Wyświetlenie wyników
print(result)
