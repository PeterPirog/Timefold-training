import pandas as pd
from ortools.sat.python import cp_model

# Zakładamy, że masz funkcję, która pobiera dane techników i urządzeń
from tools.df_merges import get_technician_and_device_data

# Pobranie danych techników i urządzeń
technicians_df, devices_df = get_technician_and_device_data()

print(technicians_df.head())
print(devices_df.head())

# Konwersja danych techników na listę słowników
technicians = []
for index, row in technicians_df.iterrows():
    technicians.append({
        "id": row['id'],  # lub 'index' w zależności od tego, jak dane są strukturyzowane
        "name": row['name'],
        "rbh_do_zaplanowania": int(row['rbh_do_zaplanowania'] * 60),  # Zamiana godzin na minuty
        "iums": set(row['iums'])  # Przypisanie odpowiednich umiejętności
    })

# Konwersja danych przyrządów na listę słowników
devices = []
for index, row in devices_df.iterrows():
    devices.append({
        "id": row['index'],  # lub 'id' w zależności od struktury danych
        "name": row['nazwa'],
        "ium": row['ium'],
        "rbh_norma": int(row['rbh_norma'] * 60),  # Zamiana godzin na minuty
        "dni_w_om": row['dni_w_om']
    })

# Tworzenie modelu
model = cp_model.CpModel()

# Zmienne decyzyjne: przypisanie techników do przyrządów
assignment = {}
for technician in technicians:
    for device in devices:
        assignment[(technician['id'], device['id'])] = model.NewBoolVar(f"assign_{technician['id']}_{device['id']}")

# Ograniczenia Hard:
# 1. Technik nie może przekroczyć liczby dostępnych godzin pracy
for technician in technicians:
    total_hours = sum(assignment[(technician['id'], device['id'])] * device["rbh_norma"] for device in devices)
    model.Add(total_hours <= technician['rbh_do_zaplanowania'])

# 2. Technik może być przypisany tylko do przyrządów, dla których ma odpowiednie umiejętności (IUM)
for technician in technicians:
    for device in devices:
        if device["ium"] not in technician["iums"]:
            model.Add(assignment[(technician['id'], device['id'])] == 0)

# Ograniczenie: Każde urządzenie może być przypisane do jednego technika lub żadnego
for device in devices:
    model.Add(sum(assignment[(technician['id'], device['id'])] for technician in technicians) <= 1)

# Funkcja celu: minimalizacja liczby nieprzypisanych urządzeń i preferencja starszych urządzeń
objective_terms = []
for device in devices:
    assigned = sum(assignment[(technician['id'], device['id'])] for technician in technicians)
    # Nagroda za przypisanie starszych urządzeń (większa liczba dni_w_om daje większy priorytet)
    objective_terms.append(assigned * device['dni_w_om'])

# Minimalizacja liczby nieprzypisanych urządzeń (negatywne wartości)
model.Maximize(sum(objective_terms))

# Tworzenie i uruchamianie solvera
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Sprawdzenie wyniku
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print('Rozwiązanie:')
    for device in devices:
        for technician in technicians:
            if solver.BooleanValue(assignment[(technician['id'], device['id'])]):
                print(f"Technik {technician['name']} przypisany do przyrządu {device['name']} (rbh_norma: {device['rbh_norma']} min)")
else:
    print('Nie znaleziono rozwiązania.')
